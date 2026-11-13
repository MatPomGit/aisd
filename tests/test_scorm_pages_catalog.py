"""Validate the generated GitHub Pages SCORM catalog against canonical raw ZIPs."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_scorm_pages_catalog import (file_sha256, load_approved_releases,
                                       verify_approved_artifact, stage_site)
from scorm_pipeline import assessment_counts, get_data, get_tracking, open_zip, TRACKING, validate_pair
from scorm_editorial import SCORM01_RELEASE


class PagesCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = ROOT / "raw"
        cls.stage = ROOT / "build" / "scorm-pages"
        cls.catalog = json.loads(
            (cls.stage / "editor" / "catalog.json").read_text(encoding="utf-8")
        )

    def test_all_real_packages_in_catalog_and_in_numeric_order(self):
        items = self.catalog["items"]
        self.assertEqual(2, self.catalog["version"])
        self.assertEqual(list(range(1, 21)), [i["number"] for i in items])
        self.assertEqual(
            {f.name for f in self.raw.glob("*.zip")},
            {i["source_filename"] for i in items},
        )

    def test_every_published_package_is_assessment_free(self):
        for item in self.catalog["items"]:
            with self.subTest(item=item["number"]):
                name = item["filename"]
                original = self.raw / item["source_filename"]
                published = self.stage / "editor" / "packages" / name
                self.assertTrue(original.is_file())
                self.assertTrue(published.is_file())
                self.assertTrue(item["prepared"])
                self.assertTrue(item["filename"].endswith("-bez-testow.zip"))
                self.assertGreaterEqual(item["knowledge_checks_removed"], 0)
                self.assertEqual(file_sha256(original), item["source_sha256"])
                self.assertEqual(published.stat().st_size, item["bytes"])
                self.assertEqual(file_sha256(published), item["sha256"])
                approved = load_approved_releases()
                expected_overlay = (SCORM01_RELEASE if item["number"] == 1 and
                                    SCORM01_RELEASE in approved else None)
                self.assertEqual(item["editorial_overlay"], expected_overlay)
                self.assertEqual(validate_pair(original, published,
                    include_editorial=bool(expected_overlay))["status"], "PASS")
                with open_zip(published) as zf:
                    _, _, _, data = get_data(zf)
                    self.assertEqual(assessment_counts(data),
                                     {"quizzes": 0, "knowledge_checks": 0,
                                      "assessment_headings": 0})
                    self.assertEqual(get_tracking(zf.read("scormcontent/index.html").decode()),
                                     TRACKING)

    def test_release_gate_rejects_unknown_or_malformed_approvals(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "releases.json"
            for invalid in ('{}', '{"approved_releases": ["unknown"]}',
                            '{"approved_releases": [true]}',
                            '{"approved_releases": ["' + SCORM01_RELEASE +
                            '", "' + SCORM01_RELEASE + '"]}'):
                with self.subTest(config=invalid):
                    path.write_text(invalid, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_approved_releases(path)

    def test_approval_must_pin_exact_rebuilt_zip_digest(self):
        import tempfile
        good = "a" * 64
        bad = "b" * 64
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "approved-releases.json"
            record = {"release": SCORM01_RELEASE, "sha256": good}
            path.write_text(json.dumps({"approved_releases": [record]}),
                            encoding="utf-8")
            approved = load_approved_releases(path)
            self.assertEqual(approved, {SCORM01_RELEASE: good})
            verify_approved_artifact(approved, SCORM01_RELEASE, good)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                verify_approved_artifact(approved, SCORM01_RELEASE, bad)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                verify_approved_artifact({}, SCORM01_RELEASE, good)

            malformed = [
                {"release": SCORM01_RELEASE},
                {"release": SCORM01_RELEASE, "sha256": "x" * 64},
                {"release": SCORM01_RELEASE, "sha256": "A" * 64},
                {"release": SCORM01_RELEASE, "sha256": 1},
                {"release": SCORM01_RELEASE, "sha256": good, "extra": True},
                {"release": "unknown-release", "sha256": good},
            ]
            for entry in malformed:
                with self.subTest(record=entry):
                    path.write_text(json.dumps({"approved_releases": [entry]}),
                                    encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_approved_releases(path)
            path.write_text(json.dumps(
                {"approved_releases": [record, record]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_approved_releases(path)

    def test_published_packages_match_catalog_with_no_stale_files(self):
        package_dir = self.stage / "editor" / "packages"
        actual = {p.name for p in package_dir.iterdir()}
        expected = {item["filename"] for item in self.catalog["items"]}
        self.assertEqual(actual, expected)

    def test_staging_rejects_wrong_approved_zip_and_discards_stale_packages(self):
        import shutil
        import tempfile
        from unittest.mock import patch

        # Use one real SCORM 01 source. The minimal staging fixture tests the
        # production stage_site path rather than only its digest helper.
        source = next(self.raw.glob("1-*.zip"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "raw"
            docs = root / "docs"
            target = root / "site"
            raw.mkdir()
            stale = docs / "editor" / "packages"
            stale.mkdir(parents=True)
            (stale / "stale-unapproved.zip").write_bytes(b"old bytes")
            shutil.copy2(source, raw / source.name)

            with patch("build_scorm_pages_catalog.load_approved_releases",
                       return_value={SCORM01_RELEASE: "f" * 64}):
                with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                    stage_site(raw, docs, target)

            with patch("build_scorm_pages_catalog.load_approved_releases",
                       return_value={}):
                catalog = stage_site(raw, docs, target)

            names = {p.name for p in
                     (target / "editor" / "packages").iterdir()}
            self.assertEqual(names, {catalog["items"][0]["filename"]})
            self.assertNotIn("stale-unapproved.zip", names)
            self.assertIsNone(catalog["items"][0]["editorial_overlay"])

    def test_scorm01_draft_is_not_in_public_catalog(self):
        if SCORM01_RELEASE in load_approved_releases():
            self.skipTest("SCORM 01 release explicitly approved")
        course = next(i for i in self.catalog["items"] if i["number"] == 1)
        self.assertIsNone(course["editorial_overlay"])

    def test_catalog_urls_resolve_only_to_relative_packages(self):
        for item in self.catalog["items"]:
            with self.subTest(item=item["number"]):
                self.assertEqual(
                    "./packages/" + item["filename"],
                    unquote(item["url"]),
                )
                self.assertTrue(item["title"])
                self.assertGreater(item["lessons"], 0)

    def test_website_preserves_expected_static_files(self):
        for path in ("index.html", ".nojekyll", "editor/index.html",
                     "editor/app.mjs", "editor/core.mjs", "editor/style.css"):
            with self.subTest(path=path):
                self.assertTrue((self.stage / path).is_file())


if __name__ == "__main__":
    unittest.main()

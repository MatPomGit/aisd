"""Validate the generated GitHub Pages SCORM catalog against canonical raw ZIPs."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_scorm_pages_catalog import file_sha256


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
        self.assertEqual(1, self.catalog["version"])
        self.assertEqual(list(range(1, 21)), [i["number"] for i in items])
        self.assertEqual(
            {f.name for f in self.raw.glob("*.zip")},
            {i["filename"] for i in items},
        )

    def test_every_published_package_matches_original_bytes(self):
        for item in self.catalog["items"]:
            with self.subTest(item=item["number"]):
                name = item["filename"]
                original = self.raw / name
                published = self.stage / "editor" / "packages" / name
                self.assertTrue(original.is_file())
                self.assertTrue(published.is_file())
                self.assertEqual(original.stat().st_size, item["bytes"])
                self.assertEqual(published.stat().st_size, item["bytes"])
                self.assertEqual(file_sha256(original), item["sha256"])
                self.assertEqual(file_sha256(published), item["sha256"])

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

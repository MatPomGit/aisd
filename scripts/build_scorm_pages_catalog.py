#!/usr/bin/env python3
"""Publish validated assessment-free derivatives of canonical raw Rise SCORM ZIPs.

Only the generated Pages artifact contains the cleaned packages. Original
raw/ sources are never modified and are not duplicated in Git history.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

from scorm_pipeline import assessment_counts, build_one, check_manifest, get_data, open_zip
from scorm_editorial import SCORM01_RELEASE

APPROVAL_FILE = Path(__file__).resolve().parents[1] / "editorial" / "approved-releases.json"


def load_approved_releases(path: Path = APPROVAL_FILE) -> dict[str, str]:
    """Require explicit approval of the exact rebuilt ZIP, not only its version.

    Changing editorial JSON while retaining an approved SemVer must never
    silently replace the package published on GitHub Pages.
    """
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) != {"approved_releases"}:
        raise ValueError("Invalid editorial release approval structure")
    records = config["approved_releases"]
    if not isinstance(records, list):
        raise ValueError("Expected a list of pinned editorial release records")
    approved = {}
    for record in records:
        if (not isinstance(record, dict) or
                set(record) != {"release", "sha256"}):
            raise ValueError("Approved releases require release and sha256")
        release, digest = record["release"], record["sha256"]
        if (not isinstance(release, str) or release != SCORM01_RELEASE or
                not isinstance(digest, str) or
                re.fullmatch(r"[0-9a-f]{64}", digest) is None or
                release in approved):
            raise ValueError("Unknown, malformed or duplicate editorial approval")
        approved[release] = digest
    return approved


def verify_approved_artifact(
    approved: dict[str, str], release: str, artifact_sha256: str
) -> None:
    """Fail before deployment when the accepted ZIP bytes have changed."""
    if approved.get(release) != artifact_sha256:
        raise ValueError(
            "Approved editorial ZIP SHA-256 mismatch: " + release +
            ". Re-run Moodle and visual acceptance; approve the new artifact "
            "digest in a separate release PR."
        )


def file_sha256(file: Path) -> str:
    digest = hashlib.sha256()
    with file.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stage_site(raw_dir: Path, docs_dir: Path, destination: Path) -> dict:
    raw_dir, docs_dir, destination = (p.resolve() for p in (raw_dir, docs_dir, destination))
    if not raw_dir.is_dir() or not docs_dir.is_dir():
        raise ValueError("Expected existing raw/ and docs/ directories")
    if destination == raw_dir or destination == docs_dir:
        raise ValueError("Output cannot replace source directories")
    if destination.is_relative_to(raw_dir) or destination.is_relative_to(docs_dir):
        raise ValueError("Output must be outside raw/ and docs/")
    if raw_dir.is_relative_to(destination) or docs_dir.is_relative_to(destination):
        raise ValueError("Output cannot contain the source directories")
    approved = load_approved_releases()
    archives = sorted(raw_dir.glob("*.zip"),
                      key=lambda p: (int(p.name.split("-", 1)[0]), p.name))
    if not archives:
        raise ValueError("No ZIP packages in raw/")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(docs_dir, destination, symlinks=False)
    target = destination / "editor" / "packages"
    # Never allow old files copied from docs/ to be published beside approved
    # derivatives. The catalog and the packages directory must agree exactly.
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    entries, reports, seen = [], [], set()
    for file in archives:
        match = re.match(r"^(\d+)-", file.name)
        if not match:
            raise ValueError("Expected numeric course prefix: " + file.name)
        number = int(match.group(1))
        if number in seen:
            raise ValueError("Duplicate course number: " + str(number))
        seen.add(number)
        if file.stat().st_size > 120 * 1024 * 1024:
            raise ValueError("ZIP exceeds browser editor limit: " + file.name)
        with open_zip(file) as source:
            check_manifest(source)
            _, _, _, data = get_data(source)
            settings = data["course"]["exportSettings"]
            title = settings.get("title") or data["course"].get("title")
            if not isinstance(title, str) or not title.strip():
                raise ValueError("Missing Rise title: " + file.name)
        output = target / (file.stem + "-bez-testow.zip")
        # Until manual visual and Moodle gates pass, publish the last safe
        # assessment-free derivative of SCORM 01, not its draft editorial text.
        include_editorial = number != 1 or SCORM01_RELEASE in approved
        report = build_one(file, output, include_editorial=include_editorial)
        if number == 1 and SCORM01_RELEASE in approved:
            verify_approved_artifact(approved, SCORM01_RELEASE, report["sha256"])
        with open_zip(output) as prepared_zip:
            _, _, _, prepared = get_data(prepared_zip)
            if any(assessment_counts(prepared).values()):
                raise ValueError("Assessment remains: " + file.name)
        reports.append({"number": number, **report})
        entries.append({
            "number": number,
            "title": title.strip(),
            "filename": output.name,
            "source_filename": file.name,
            "url": "./packages/" + quote(output.name, safe=""),
            "bytes": output.stat().st_size,
            "sha256": file_sha256(output),
            "source_sha256": file_sha256(file),
            "lessons": len(prepared["course"]["lessons"]),
            "prepared": True,
            "editorial_overlay": report["editorial_overlay"],
            "knowledge_checks_removed": report["knowledge_checks_removed"],
            "assessment_sections_removed": report["assessment_sections_removed"],
            "removed_quiz": bool(report["removed_quiz"]),
            "embedded_test_removed": bool(report["embedded_test_removed"]),
        })
    catalog = {
        "version": 2,
        "source": "MatPomGit/aisd/raw",
        "description": "Assessment-free SCORM derivatives",
        "items": entries,
    }
    (destination / "editor" / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "editor" / "build-report.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for entry in entries:
        copied = target / entry["filename"]
        if copied.stat().st_size != entry["bytes"] or file_sha256(copied) != entry["sha256"]:
            raise ValueError("Staged ZIP checksum mismatch: " + entry["filename"])
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=Path("raw"))
    parser.add_argument("--docs", type=Path, default=Path("docs"))
    parser.add_argument("--output", type=Path, default=Path("build/scorm-pages"))
    options = parser.parse_args()
    catalog = stage_site(options.raw, options.docs, options.output)
    print("Published " + str(len(catalog["items"])) + " assessment-free SCORM ZIPs")
    for item in catalog["items"]:
        print(f'{item["number"]:02d} | {item["title"]} | '
              f'{item["knowledge_checks_removed"]} checks removed | '
              f'{item["assessment_sections_removed"]} assessment sections | '
              f'{item["sha256"][:12]}')


if __name__ == "__main__":
    main()

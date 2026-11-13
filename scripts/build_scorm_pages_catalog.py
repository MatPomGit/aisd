#!/usr/bin/env python3
"""Stage the static SCORM Studio site and indexed original Rise ZIPs for GitHub Pages.

The original ZIPs remain in raw/; the published catalog and packages are
generated only in the Actions build directory. No Git commit or server API.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

from scorm_pipeline import check_manifest, get_data, open_zip


def stage_site(raw_dir: Path, docs_dir: Path, destination: Path) -> dict:
    raw_dir = raw_dir.resolve()
    docs_dir = docs_dir.resolve()
    destination = destination.resolve()
    if not raw_dir.is_dir() or not docs_dir.is_dir():
        raise ValueError("Expected existing raw/ and docs/ directories")
    if destination == raw_dir or destination == docs_dir:
        raise ValueError("Output cannot replace source directories")
    if destination.is_relative_to(raw_dir) or destination.is_relative_to(docs_dir):
        raise ValueError("Output must be outside raw/ and docs/")
    archives = sorted(raw_dir.glob("*.zip"), key=lambda p: (int(p.name.split("-", 1)[0]), p.name))
    if not archives:
        raise ValueError("No ZIP packages in raw/")
    entries = []
    seen = set()
    for file in archives:
        match = re.match(r"^(\d+)-", file.name)
        if not match:
            raise ValueError(f"Expected numeric course prefix: {file.name}")
        number = int(match.group(1))
        if number in seen:
            raise ValueError(f"Duplicate course number: {number}")
        seen.add(number)
        if file.stat().st_size > 120 * 1024 * 1024:
            raise ValueError(f"ZIP exceeds browser editor limit: {file.name}")
        with open_zip(file) as zf:
            check_manifest(zf)
            _, _, _, data = get_data(zf)
            settings = data["course"]["exportSettings"]
            title = settings.get("title") or data["course"].get("title")
            if not isinstance(title, str) or not title.strip():
                raise ValueError(f"Missing Rise title: {file.name}")
            entries.append({
                "number": number,
                "title": title.strip(),
                "filename": file.name,
                "url": "./packages/" + quote(file.name, safe=""),
                "bytes": file.stat().st_size,
                "sha256": file_sha256(file),
                "lessons": len(data["course"]["lessons"]),
            })
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(docs_dir, destination, symlinks=False)
    target_dir = destination / "editor" / "packages"
    target_dir.mkdir(parents=True, exist_ok=True)
    for file in archives:
        shutil.copyfile(file, target_dir / file.name)
    catalog = {"version": 1, "source": "MatPomGit/aisd/raw", "items": entries}
    (destination / "editor" / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for item in entries:
        copied = target_dir / item["filename"]
        if copied.stat().st_size != item["bytes"] or file_sha256(copied) != item["sha256"]:
            raise ValueError("Staged ZIP differs from raw: " + item["filename"])
    return catalog


def file_sha256(file: Path) -> str:
    digest = hashlib.sha256()
    with file.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=Path("raw"))
    parser.add_argument("--docs", type=Path, default=Path("docs"))
    parser.add_argument("--output", type=Path, default=Path("build/scorm-pages"))
    options = parser.parse_args()
    catalog = stage_site(options.raw, options.docs, options.output)
    print(f"Staged {len(catalog['items'])} SCORM ZIPs at {options.output}")
    for item in catalog["items"]:
        print(f"{item['number']:02d} | {item['title']} | {item['bytes']} B | {item['sha256'][:12]}")


if __name__ == "__main__":
    main()

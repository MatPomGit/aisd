#!/usr/bin/env python3
"""Deterministic, reproducible structural/content QA for a revised Rise SCORM 01 ZIP.

This is not a substitute for factual review of each assertion, accessibility
assistive-technology testing, or a real Moodle integration test.
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scorm_pipeline import (open_zip, get_data, check_manifest,
                            unlisted_manifest_files, assessment_counts)


class FragmentParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.issues = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)
        if tag == "img":
            attributes = dict(attrs)
            if not attributes.get("alt", "").strip():
                self.issues.append("Image without nonempty alt text")
        if tag == "a" and not dict(attrs).get("href", "").strip():
            self.issues.append("Anchor without href")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.issues.append("Unexpected HTML closing tag: " + tag)
        else:
            self.stack.pop()

    def finish(self):
        self.close()
        if self.stack:
            self.issues.append("Unclosed HTML tags: " + ",".join(self.stack))
        return self.issues


def audit(path):
    findings = []
    inventory = []
    with open_zip(path) as zf:
        check_manifest(zf)
        omissions = unlisted_manifest_files(zf)
        if omissions:
            findings.append({"severity": "P0", "location": "imsmanifest.xml",
                             "message": "Unlisted packaged files", "files": omissions})
        _, _, _, data = get_data(zf)
    lessons = data["course"]["lessons"]
    counts = assessment_counts(data)
    if any(counts.values()):
        findings.append({"severity": "P0", "location": "course",
                         "message": "Assessment elements still present",
                         "counts": counts})
    if len(lessons) != 11:
        findings.append({"severity": "P0", "location": "course",
                         "message": "Expected exactly 11 lessons"})
    all_ids = []
    total_fragments = 0
    for index, lesson in enumerate(lessons, 1):
        blocks = lesson.get("items", [])
        stats = {"lesson": index, "id": lesson.get("id"),
                 "title": lesson.get("title"), "blocks": len(blocks),
                 "html_fragments": 0, "interactive_rows": 0,
                 "characters": 0}
        if not isinstance(blocks, list) or not blocks:
            findings.append({"severity": "P0", "location": f"lesson-{index:02d}",
                             "message": "Missing content blocks"})
            continue
        for block in blocks:
            location = f"lesson-{index:02d}/{block.get('id', '<missing>')}"
            all_ids.append((location, block.get("id")))
            if not isinstance(block.get("id"), str) or not block["id"]:
                findings.append({"severity": "P0", "location": location,
                                 "message": "Invalid block identifier"})
            rows = block.get("items", [])
            if not isinstance(rows, list):
                findings.append({"severity": "P0", "location": location,
                                 "message": "Block rows are not a list"})
                continue
            if block.get("type") == "interactive":
                stats["interactive_rows"] += len(rows)
                if not rows:
                    findings.append({"severity": "P1", "location": location,
                                     "message": "Empty interactive block"})
            for row_index, row in enumerate(rows):
                if not isinstance(row, dict):
                    findings.append({"severity": "P0", "location": location,
                                     "message": "Non-object content row"})
                    continue
                for field in ("heading", "paragraph", "description", "title"):
                    value = row.get(field)
                    if not isinstance(value, str):
                        continue
                    stats["characters"] += len(value)
                    if not value.strip():
                        # Rise heading rows may carry a deliberately blank
                        # optional paragraph; the visible heading supplies
                        # actual content. Do not report that as a missing block.
                        if field == "paragraph" and isinstance(row.get("heading"), str) \
                                and row["heading"].strip():
                            continue
                        # Rise image/hero rows contain a blank auxiliary
                        # paragraph with the actual image in media.image.
                        if (field == "paragraph" and block.get("type") == "image"
                                and block.get("variant") == "hero"
                                and isinstance(row.get("media"), dict)
                                and isinstance(row["media"].get("image"), dict)
                                and bool(row["media"]["image"].get("key"))):
                            continue
                        findings.append({"severity": "P1", "location":
                                         f"{location}/row-{row_index}/{field}",
                                         "message": "Empty content field",
                                         "block_type": block.get("type"),
                                         "block_variant": block.get("variant"),
                                         "row_fields": {k: str(v)[:80] for k, v
                                                        in row.items()}})
                        continue
                    if "<" in value or "&" in value:
                        parser = FragmentParser()
                        parser.feed(value)
                        for problem in parser.finish():
                            findings.append({"severity": "P1", "location":
                                             f"{location}/row-{row_index}/{field}",
                                             "message": problem})
                        stats["html_fragments"] += 1
                        total_fragments += 1
                    if re.search(r"<script\b|javascript\s*:", value, re.I):
                        findings.append({"severity": "P0", "location":
                                         f"{location}/row-{row_index}/{field}",
                                         "message": "Executable markup in instructional text"})
        inventory.append(stats)
    identifiers = [identity for _, identity in all_ids]
    if len(identifiers) != len(set(identifiers)):
        findings.append({"severity": "P1", "location": "course",
                         "message": "Repeated block identifiers across lessons"})
    return {
        "schema_version": 1,
        "scope": "automated-structural-content-audit-not-independent-scientific-proof",
        "package": path.name,
        "lessons_checked": len(lessons),
        "blocks_checked": sum(x["blocks"] for x in inventory),
        "html_fragments_checked": total_fragments,
        "interactive_rows_checked": sum(x["interactive_rows"] for x in inventory),
        "assessment_counts": counts,
        "lessons": inventory,
        "findings": findings,
        "result": "PASS" if not findings else "FAIL"
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.package)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({key: result[key] for key in
                      ("result", "lessons_checked", "blocks_checked",
                       "html_fragments_checked", "interactive_rows_checked",
                       "findings")}, ensure_ascii=False))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

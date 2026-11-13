"""Deterministic, fail-closed editorial overlays for Rise SCORM data.

Overlays operate on the decoded course JSON AFTER assessment removal and BEFORE
re-encoding the ZIP. No edits to binary sources, manifests or identifiers.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORM01_OVERLAY = ROOT / "editorial" / "scorm01" / "lesson-01.json"
SCORM01_COURSE_ID = "SZEbwB8BnpsJ5CIenO-FYt21dzH6nrro"


class EditorialError(ValueError):
    """Refuse editorial changes on an unexpected Rise structure."""


def require(predicate: bool, reason: str) -> None:
    if not predicate:
        raise EditorialError(reason)


def apply_editorial(data: dict) -> dict | None:
    """Apply only known course overlays; return an audit summary or None."""
    course = data.get("course")
    if not isinstance(course, dict) or course.get("id") != SCORM01_COURSE_ID:
        return None
    overlay = json.loads(SCORM01_OVERLAY.read_text(encoding="utf-8"))
    require(overlay["schema_version"] == 1, "Unsupported editorial overlay schema")
    require(overlay["course_id"] == course["id"], "Editorial course ID mismatch")
    require(overlay["course_title"] == course.get("title"), "Editorial course title changed")
    lessons = course.get("lessons")
    require(isinstance(lessons, list) and bool(lessons), "No lessons in course 01")
    lesson = lessons[0]
    require(lesson.get("id") == overlay["lesson_id"], "Introductory lesson ID changed")
    require(lesson.get("title") == overlay["expected_lesson_title"],
            "Introductory lesson title changed")
    blocks = lesson.get("items")
    require(isinstance(blocks, list), "Unexpected lesson blocks")
    ids = [b.get("id") for b in blocks if isinstance(b, dict)]
    require(len(ids) == len(blocks), "Invalid Rise block")
    require(ids == overlay["expected_block_ids"],
            "Source block IDs/order differ; do not apply speculative patch")

    keep_ids = overlay["keep_block_ids"]
    require(len(set(keep_ids)) == len(keep_ids), "Duplicate keep ID")
    require(all(i in ids for i in keep_ids), "Unknown keep ID")
    require([i for i in ids if i in keep_ids] == keep_ids, "Keep order has changed")
    updates = overlay["updates"]
    require(set(updates).issubset(set(keep_ids)), "Updates target removed blocks")

    kept = [block for block in blocks if block["id"] in keep_ids]
    index = {block["id"]: block for block in kept}
    for block_id, change in updates.items():
        block = index[block_id]
        kind = block.get("type")
        variant = block.get("variant")
        rows = block.get("items")
        require(isinstance(rows, list) and bool(rows), "Missing Rise block items")
        if set(change).issubset({"heading", "paragraph"}) and change:
            require(kind == "text" and len(rows) == 1,
                    "Text edit does not target a single text item")
            for key, value in change.items():
                require(key in rows[0] and isinstance(value, str),
                        "Text field missing from Rise item: " + key)
                rows[0][key] = value
        elif set(change) == {"list_paragraphs"}:
            values = change["list_paragraphs"]
            require(kind == "list" and variant == "numbered" and
                    isinstance(values, list) and len(values) == len(rows),
                    "Unexpected numbered-list layout")
            for row, value in zip(rows, values):
                require("paragraph" in row and isinstance(value, str),
                        "Unexpected numbered list item")
                row["paragraph"] = value
        elif set(change) == {"accordion_entries"}:
            values = change["accordion_entries"]
            require(kind == "interactive" and variant == "accordion" and
                    isinstance(values, list) and len(values) == len(rows),
                    "Unexpected accordion layout")
            for row, value in zip(rows, values):
                require(set(value) == {"title", "description"} and
                        "title" in row and "description" in row,
                        "Unexpected accordion item")
                for key, text in value.items():
                    require(isinstance(text, str), "Invalid accordion text")
                    row[key] = text
        else:
            raise EditorialError("Unsupported editorial operation: " + block_id)

    require(all("<script" not in str(v).lower() for v in updates.values()),
            "Embedded script in editorial text")
    lesson["items"] = kept
    return {
        "course": 1,
        "lesson_id": lesson["id"],
        "overlay_version": overlay["revision"],
        "edited_blocks": len(updates),
        "removed_redundant_blocks": len(blocks) - len(kept),
    }

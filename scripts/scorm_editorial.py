"""Versioned, fail-closed editorial overlays for Articulate Rise SCORM 01.

Text-only overlays operate after knowledge-check removal and before re-encoding.
They preserve source ZIP, lesson IDs and media, and reject unexpected layouts.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORM01_DIR = ROOT / "editorial" / "scorm01"
SCORM01_COURSE_ID = "SZEbwB8BnpsJ5CIenO-FYt21dzH6nrro"
SCORM01_LESSON_FILES = tuple(
    SCORM01_DIR / f"lesson-{index:02d}.json" for index in range(1, 12)
)
SCORM01_RELEASE = "scorm01/lessons-01-11@2.0.0"


class EditorialError(ValueError):
    """Unknown or changed Rise structure: do not publish a speculative edit."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise EditorialError(reason)


def _apply_lesson(course: dict, overlay: dict) -> dict:
    require(overlay.get("schema_version") == 1,
            "Unsupported editorial overlay schema")
    require(overlay.get("course_id") == course["id"],
            "Editorial course ID mismatch")
    require(overlay.get("course_title") == course.get("title"),
            "Editorial course title changed")
    index = overlay.get("lesson_index", 0)
    lessons = course.get("lessons")
    require(isinstance(index, int) and not isinstance(index, bool) and
            isinstance(lessons, list) and 0 <= index < len(lessons),
            "Invalid target lesson index")
    lesson = lessons[index]
    require(lesson.get("id") == overlay.get("lesson_id"),
            f"Lesson ID changed: {index + 1}")
    require(lesson.get("title") == overlay.get("expected_lesson_title"),
            f"Lesson title changed: {index + 1}")
    blocks = lesson.get("items")
    require(isinstance(blocks, list), "Unexpected lesson blocks")
    require(all(isinstance(b, dict) and isinstance(b.get("id"), str)
                for b in blocks), "Invalid Rise block")
    ids = [b["id"] for b in blocks]
    require(len(set(ids)) == len(ids), "Duplicate block ID")
    require(ids == overlay.get("expected_block_ids"),
            f"Source block IDs/order differ in lesson {index + 1}")

    keep_ids = overlay.get("keep_block_ids")
    changes = overlay.get("updates")
    require(isinstance(keep_ids, list) and bool(keep_ids) and
            isinstance(changes, dict), "Invalid overlay changes")
    require(len(set(keep_ids)) == len(keep_ids), "Duplicate keep ID")
    require([i for i in ids if i in set(keep_ids)] == keep_ids,
            "Unexpected keep-list order or unknown ID")
    require(set(changes).issubset(set(keep_ids)),
            "Updates refer to a removed block")
    expected_rows = overlay.get("expected_interactive_rows")
    require(isinstance(expected_rows, dict),
            "Missing interactive source-row identities")
    interactive_keys = {"accordion_entries", "tabs_entries", "process_entries"}
    interactive_ids = {block_id for block_id, change in changes.items()
                       if isinstance(change, dict) and
                       bool(set(change) & interactive_keys)}
    require(set(expected_rows) == interactive_ids,
            "Missing or extra interactive row identity assertions")
    edited = [b for b in blocks if b["id"] in set(keep_ids)]
    by_id = {b["id"]: b for b in edited}

    for block_id, change in changes.items():
        block = by_id[block_id]
        kind, variant = block.get("type"), block.get("variant")
        rows = block.get("items")
        require(isinstance(change, dict) and isinstance(rows, list) and bool(rows),
                "Missing Rise block items")
        if set(change) in ({"paragraph"}, {"heading"}, {"heading", "paragraph"}):
            require(kind == "text" and len(rows) == 1,
                    "Text edit does not target a single text item")
            for key, value in change.items():
                require(key in rows[0] and isinstance(value, str) and value.strip(),
                        "Text field missing or empty: " + key)
                rows[0][key] = value
        elif set(change) == {"list_paragraphs"}:
            values = change["list_paragraphs"]
            require(kind == "list" and variant == "numbered" and
                    isinstance(values, list) and len(values) == len(rows),
                    "Unexpected numbered-list layout")
            for row, value in zip(rows, values):
                require("paragraph" in row and isinstance(value, str) and value.strip(),
                        "Unexpected numbered-list item")
                row["paragraph"] = value
        elif set(change) in ({"accordion_entries"}, {"tabs_entries"}, {"process_entries"}):
            key = next(iter(change))
            expected = {
                "accordion_entries": "accordion",
                "tabs_entries": "tabs",
                "process_entries": "process",
            }[key]
            values = change[key]
            require(kind == "interactive" and variant == expected and
                    isinstance(values, list) and len(values) == len(rows),
                    "Unexpected interactive layout: " + expected)
            if expected == "process":
                # Rise renders intro first, step rows next, and summary last.
                # Their serialized position differs from the displayed order.
                require([row.get("type") for row in rows] ==
                        ["intro", "summary"] + ["step"] * (len(rows) - 2),
                        "Unexpected Rise process intro/summary/step roles")
            source_rows = expected_rows[block_id]
            require(isinstance(source_rows, list) and
                    all(isinstance(r, dict) and
                        set(r) == {"id", "title"} and
                        isinstance(r["id"], str) and
                        isinstance(r["title"], str) for r in source_rows) and
                    [{"id": r.get("id"), "title": r.get("title")} for r in rows]
                    == source_rows,
                    "Interactive source row identity/order changed: " + block_id)
            for row, value in zip(rows, values):
                require(isinstance(value, dict) and
                        set(value) == {"title", "description"} and
                        all(key in row for key in ("title", "description")),
                        "Unexpected interactive item")
                for field, txt in value.items():
                    require(isinstance(txt, str) and txt.strip(),
                            "Empty interactive text")
                    row[field] = txt
        else:
            raise EditorialError("Unsupported editorial operation: " + block_id)

    require("<script" not in json.dumps(changes, ensure_ascii=False).lower(),
            "Embedded script in editorial content")
    title = overlay.get("new_lesson_title")
    if title is not None:
        require(isinstance(title, str) and title.strip(),
                "Invalid new lesson title")
        lesson["title"] = title
    lesson["items"] = edited
    return {
        "lesson_index": index,
        "lesson_id": lesson["id"],
        "version": overlay["revision"],
        "updated_blocks": len(changes),
        "removed_redundant_blocks": len(blocks) - len(edited),
    }


def apply_editorial(data: dict) -> list[dict] | None:
    """Modify a known course in-place, or return None without changes.

    Every file is required for SCORM 01. Callers must work on a deep copy:
    if a later lesson fails its structural checks, the entire build is aborted.
    """
    course = data.get("course")
    if not isinstance(course, dict) or course.get("id") != SCORM01_COURSE_ID:
        return None
    results = []
    for expected_index, path in enumerate(SCORM01_LESSON_FILES):
        try:
            overlay = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EditorialError(f"Cannot read overlay {path.name}: {exc}") from exc
        require(overlay.get("lesson_index", 0) == expected_index,
                f"Overlay targets wrong lesson: {path.name}")
        results.append(_apply_lesson(course, overlay))
    return results

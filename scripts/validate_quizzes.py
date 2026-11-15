#!/usr/bin/env python3
"""Statyczna kontrola oddzielnych banków pytań GIFT W01-W20.

Nie jest to parser pełnego formatu GIFT ani weryfikator merytoryczny.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZZES = ROOT / "quizzes"
QUESTION = re.compile(r"^::AISD-(\d{2})-Q(\d{2})::(.+) \{$")
CHOICE = re.compile(r"^  ([=~])(.+)$")
FEEDBACK = re.compile(r"^  ####(.+)$")
EXPECTED_LECTURES = 20
EXPECTED_QUESTIONS = 8


def inspect_file(path: Path, lecture: int) -> list[str]:
    errors: list[str] = []
    content = path.read_text(encoding="utf-8")
    chunks = re.split(r"(?=^::AISD-\d{2}-Q\d{2}::)", content, flags=re.MULTILINE)[1:]
    if len(chunks) != EXPECTED_QUESTIONS:
        errors.append(f"{path}: expected {EXPECTED_QUESTIONS} questions, got {len(chunks)}")
    ids: set[str] = set()
    for position, chunk in enumerate(chunks, start=1):
        lines = chunk.splitlines()
        match = QUESTION.fullmatch(lines[0]) if lines else None
        if not match:
            errors.append(f"{path}: invalid GIFT header in item {position}")
            continue
        lno, qno, stem = match.groups()
        expected = f"{lecture:02d}-{position:02d}"
        if f"{lno}-{qno}" != expected:
            errors.append(f"{path}: unexpected identifier {lno}-{qno}, expected {expected}")
        if not stem.strip():
            errors.append(f"{path}: empty question {position}")
        key = f"{lno}-{qno}"
        if key in ids:
            errors.append(f"{path}: duplicate question identifier {key}")
        ids.add(key)
        if not [line.strip() for line in lines if line.strip()][-1:] == ["}"]:
            errors.append(f"{path}: missing answer block terminator in {key}")
        options = [x for x in lines if CHOICE.fullmatch(x)]
        correct = [x for x in options if x.startswith("  =")]
        wrong = [x for x in options if x.startswith("  ~")]
        feedback = [x for x in lines if FEEDBACK.fullmatch(x)]
        if len(options) != 4 or len(correct) != 1 or len(wrong) != 3:
            errors.append(f"{path}: {key} needs 4 choices including exactly one correct")
        if len(feedback) != 1 or not FEEDBACK.fullmatch(feedback[0]):
            errors.append(f"{path}: {key} needs exactly one explanatory feedback")
        normalized = [re.sub(r"\\([~=#{}\\])", r"\1", x[3:]).strip() for x in options]
        if len(set(normalized)) != len(normalized):
            errors.append(f"{path}: {key} contains duplicate answers")
    return errors


def main() -> int:
    errors: list[str] = []
    expected_names = {f"quiz_w{i:02d}.gift" for i in range(1, EXPECTED_LECTURES + 1)}
    actual_names = {p.name for p in QUIZZES.glob("*.gift")}
    for name in sorted(expected_names - actual_names):
        errors.append(f"missing: {name}")
    for name in sorted(actual_names - expected_names):
        errors.append(f"unexpected: {name}")
    for i in range(1, EXPECTED_LECTURES + 1):
        path = QUIZZES / f"quiz_w{i:02d}.gift"
        if path.is_file():
            errors.extend(inspect_file(path, i))
    if errors:
        print("\n".join(f"FAIL: {msg}" for msg in errors))
        return 1
    print(f"PASS: {EXPECTED_LECTURES} banks, {EXPECTED_LECTURES * EXPECTED_QUESTIONS} GIFT questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())

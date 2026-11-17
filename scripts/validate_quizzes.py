#!/usr/bin/env python3
"""Statyczna kontrola 20 banków pytań Moodle GIFT.

Sprawdza strukturę pytań, kodowanie UTF-8 oraz zapis znaków sterujących
GIFT. Nie zastępuje importu do Moodle ani recenzji merytorycznej.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZZES = ROOT / "quizzes"
QUESTION = re.compile(r"^::AISD-(\d{2})-Q(\d{2})::\[plain\](.+) \{$")
CHOICE = re.compile(r"^  ([=~])(.+)$")
FEEDBACK = re.compile(r"^  ####(.+)$")
EXPECTED_LECTURES = 20
EXPECTED_QUESTIONS = 20
GIFT_CONTROL = frozenset("~=#{}")
INVISIBLE_OR_INVALID = frozenset("\u00a0\u200b\u200c\u200d\ufeff\ufffd")


def check_gift_text(value: str, location: str) -> list[str]:
    """Sprawdza, czy tekst nie zawiera surowych separatorów GIFT."""
    errors: list[str] = []
    if any(char in INVISIBLE_OR_INVALID for char in value):
        errors.append(f"{location}: niewidoczny lub zastępczy znak Unicode")
    if unicodedata.normalize("NFC", value) != value:
        errors.append(f"{location}: tekst nie jest znormalizowany do NFC")
    index = 0
    while index < len(value):
        char = value[index]
        if char == "\\":
            if index + 1 >= len(value) or value[index + 1] not in GIFT_CONTROL | {"\\"}:
                errors.append(f"{location}: nieprawidłowa sekwencja z odwrotnym ukośnikiem")
                break
            index += 2
            continue
        if char in GIFT_CONTROL:
            errors.append(f"{location}: niepoprzedzony ukośnikiem znak sterujący {char!r}")
            break
        index += 1
    return errors


def inspect_file(path: Path, lecture: int) -> list[str]:
    errors: list[str] = []
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{path}: plik UTF-8 nie może mieć znacznika BOM")
    try:
        content = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        return [f"{path}: nieprawidłowe kodowanie UTF-8: {exc}"]

    chunks = re.split(r"(?=^::AISD-\d{2}-Q\d{2}::)", content, flags=re.MULTILINE)[1:]
    if len(chunks) != EXPECTED_QUESTIONS:
        errors.append(f"{path}: oczekiwano {EXPECTED_QUESTIONS} pytań, znaleziono {len(chunks)}")
    ids: set[str] = set()
    stems: set[str] = set()
    key_positions = [0, 0, 0, 0]

    for position, chunk in enumerate(chunks, start=1):
        lines = chunk.splitlines()
        match = QUESTION.fullmatch(lines[0]) if lines else None
        if not match:
            errors.append(f"{path}: błędny nagłówek GIFT pytania {position}; wymagane [plain]")
            continue
        lno, qno, stem = match.groups()
        key = f"{lno}-{qno}"
        expected = f"{lecture:02d}-{position:02d}"
        if key != expected:
            errors.append(f"{path}: identyfikator {key}, oczekiwano {expected}")
        if key in ids:
            errors.append(f"{path}: powtórzony identyfikator {key}")
        ids.add(key)
        if not stem.strip():
            errors.append(f"{path}: pytanie {key} jest puste")
        normalized_stem = stem.strip()
        if normalized_stem in stems:
            errors.append(f"{path}: powtórzona treść pytania {key}")
        stems.add(normalized_stem)
        errors.extend(check_gift_text(stem, f"{path}: {key}: treść"))

        nonempty = [line.strip() for line in lines if line.strip()]
        if not nonempty or nonempty[-1] != "}":
            errors.append(f"{path}: brak zakończenia bloku odpowiedzi w {key}")

        options = [line for line in lines if CHOICE.fullmatch(line)]
        correct = [line for line in options if line.startswith("  =")]
        wrong = [line for line in options if line.startswith("  ~")]
        feedback = [line for line in lines if FEEDBACK.fullmatch(line)]
        if len(options) != 4 or len(correct) != 1 or len(wrong) != 3:
            errors.append(f"{path}: {key} musi mieć cztery warianty i dokładnie jeden klucz")
        else:
            key_positions[options.index(correct[0])] += 1
        if len(feedback) != 1:
            errors.append(f"{path}: {key} wymaga jednego uzasadnienia")

        # Notacja asymptotyczna O(n) i o(n) jest rozróżniana wielkością liter.
        # Nie używamy casefold(), bo zmieniłoby znaczenie odpowiedzi.
        choices: list[str] = []
        for option in options:
            value = option[3:]
            errors.extend(check_gift_text(value, f"{path}: {key}: wariant"))
            choices.append(re.sub(r"\\([~=#{}\\])", r"\1", value).strip())
        if len(set(choices)) != len(choices):
            errors.append(f"{path}: {key} zawiera powtórzone warianty")

        for item in feedback:
            errors.extend(check_gift_text(item[6:], f"{path}: {key}: uzasadnienie"))

    if key_positions != [EXPECTED_QUESTIONS // 4] * 4:
        errors.append(f"{path}: nierówny rozkład pozycji klucza: {key_positions}")
    return errors


def main() -> int:
    errors: list[str] = []
    expected_names = {f"quiz_w{i:02d}.gift" for i in range(1, EXPECTED_LECTURES + 1)}
    actual_names = {p.name for p in QUIZZES.glob("*.gift")}
    for name in sorted(expected_names - actual_names):
        errors.append(f"Brak pliku: {name}")
    for name in sorted(actual_names - expected_names):
        errors.append(f"Nieoczekiwany plik: {name}")
    for i in range(1, EXPECTED_LECTURES + 1):
        path = QUIZZES / f"quiz_w{i:02d}.gift"
        if path.is_file():
            errors.extend(inspect_file(path, i))
    if errors:
        print("\n".join(f"BŁĄD: {message}" for message in errors))
        return 1
    print(f"PASS: {EXPECTED_LECTURES} banków, {EXPECTED_LECTURES * EXPECTED_QUESTIONS} pytań GIFT (UTF-8, [plain])")
    return 0


if __name__ == "__main__":
    sys.exit(main())

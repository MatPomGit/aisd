#!/usr/bin/env python3
"""Statyczna kontrola 20 banków pytań Moodle GIFT (jedno- i wielokrotny wybór).

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
CHOICE = re.compile(r"^  ([=~])(?:%(-?\d+(?:\.\d+)?)%)?(.+)$")
FEEDBACK = re.compile(r"^  ####(.+)$")
EXPECTED_LECTURES = 20
EXPECTED_QUESTIONS = 20
GIFT_CONTROL = frozenset("~=#{}")
INVISIBLE_OR_INVALID = frozenset("\u00a0\u200b\u200c\u200d\ufeff\ufffd")
UNFINISHED_ANSWER = re.compile(
    r"(?:tylko wtedy|również wtedy|jedynie wtedy|wyłącznie|tylko gdy|jedynie gdy|pod warunkiem)\.?$",
    flags=re.IGNORECASE,
)


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
    key_sequence: list[int | None] = []
    multiple_questions = 0

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

        raw_options = [line for line in lines if line.startswith(("  =", "  ~"))]
        options = [CHOICE.fullmatch(line) for line in raw_options]
        feedback = [line for line in lines if FEEDBACK.fullmatch(line)]
        key_sequence.append(None)
        if len(raw_options) != 4 or any(item is None for item in options):
            errors.append(f"{path}: {key} wymaga czterech poprawnych składniowo wariantów GIFT")
            continue
        weighted = any(item.group(2) is not None for item in options)
        if weighted:
            multiple_questions += 1
            weights = [float(item.group(2)) if item.group(2) is not None else None
                       for item in options]
            positives = [weight for weight in weights if weight is not None and weight > 0]
            negatives = [weight for weight in weights if weight is not None and weight < 0]
            if (any(item.group(1) != "~" for item in options)
                    or any(weight is None or weight == 0 for weight in weights)
                    or len(positives) < 2 or len(negatives) < 1
                    or abs(sum(positives) - 100) > 0.01
                    or sum(negatives) > -99.99):
                errors.append(f"{path}: {key} niepoprawne wagi wielokrotnego wyboru")
            if "Zaznacz wszystkie poprawne odpowiedzi" not in stem:
                errors.append(f"{path}: {key} brak jawnego polecenia wielokrotnego wyboru")
        else:
            correct = [i for i, item in enumerate(options) if item.group(1) == "="]
            if len(correct) != 1:
                errors.append(f"{path}: {key} musi mieć dokładnie jeden klucz jednokrotnego wyboru")
            else:
                key_positions[correct[0]] += 1
                key_sequence[-1] = correct[0]
        if len(feedback) != 1:
            errors.append(f"{path}: {key} wymaga jednego uzasadnienia")

        # Notacja asymptotyczna O(n) i o(n) jest rozróżniana wielkością liter.
        # Nie używamy casefold(), bo zmieniłoby znaczenie odpowiedzi.
        choices: list[str] = []
        for option in options:
            value = option.group(3)
            errors.extend(check_gift_text(value, f"{path}: {key}: wariant"))
            choices.append(re.sub(r"\\([~=#{}\\])", r"\1", value).strip())
        if len(set(choices)) != len(choices):
            errors.append(f"{path}: {key} zawiera powtórzone warianty")
        if any(UNFINISHED_ANSWER.search(answer) for answer in choices):
            errors.append(f"{path}: {key} zawiera urwany wariant odpowiedzi")
        for short in ("Tak", "Nie"):
            if short in {answer.rstrip(".").strip() for answer in choices}:
                if any(answer.startswith(short + ",") for answer in choices):
                    errors.append(f"{path}: {key} zawiera dwie odpowiedzi o tej samej wartości logicznej")

        for item in feedback:
            errors.extend(check_gift_text(item[6:], f"{path}: {key}: uzasadnienie"))

    if multiple_questions == 0:
        if key_positions != [EXPECTED_QUESTIONS // 4] * 4:
            errors.append(f"{path}: nierówny rozkład pozycji klucza: {key_positions}")
    elif max(key_positions) - min(key_positions) > 2:
        errors.append(f"{path}: nierówny rozkład kluczy jednokrotnego wyboru: {key_positions}")
    if len(key_sequence) == EXPECTED_QUESTIONS:
        if any(key_sequence[i] is not None
               and key_sequence[i] == key_sequence[i - 1] == key_sequence[i - 2]
               for i in range(2, EXPECTED_QUESTIONS)):
            errors.append(f"{path}: trzy identyczne pozycje klucza z rzędu")
        if multiple_questions == 0 and any(
                all(key_sequence[i] == key_sequence[i - period]
                    for i in range(period, EXPECTED_QUESTIONS))
                for period in range(1, EXPECTED_QUESTIONS // 2 + 1)):
            errors.append(f"{path}: okresowy, przewidywalny klucz odpowiedzi")
        if any(all(key_sequence[i + j] is not None
                   and key_sequence[i + j + 2] is not None
                   and key_sequence[i + j] == key_sequence[i + j + 2]
                   for j in range(4))
               for i in range(EXPECTED_QUESTIONS - 5)):
            errors.append(f"{path}: sześć kolejnych pozycji z naprzemiennym wzorcem klucza")
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
    multiple = sum(
        "Zaznacz wszystkie poprawne odpowiedzi" in line
        for path in QUIZZES.glob("*.gift")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("::AISD-")
    )
    print(f"PASS: {EXPECTED_LECTURES} banków, {EXPECTED_LECTURES * EXPECTED_QUESTIONS} pytań GIFT, w tym {multiple} wielokrotnego wyboru (UTF-8, [plain])")
    return 0


if __name__ == "__main__":
    sys.exit(main())

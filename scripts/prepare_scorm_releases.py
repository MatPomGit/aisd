#!/usr/bin/env python3
"""Prepare Polish GitHub Release metadata for validated SCORM 1.2 packages.

Only produces local text and JSON. The release workflow publishes the artifacts.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

DISALLOWED = re.compile(r"[\u2010-\u2015\u2212]")

def notes(number, title, version, source, sha):
    heading = f"SCORM {number:02d}: {title}. Wersja {version}"
    paragraphs = [
        heading,
        "",
        "Pakiet dydaktyczny w standardzie SCORM 1.2 przeznaczony do platform LMS.",
        "Wersja nie zawiera testów końcowych ani pytań kontrolnych.",
        "Zastosowano zabezpieczenie przed wznowieniem kursu na usuniętej lekcji.",
        "Nieaktualny adres lekcji powoduje otwarcie strony początkowej,",
        "bez usuwania zapisanych danych postępu.",
        "",
        "Kontrole: poprawność archiwum ZIP, manifest SCORM, kompletność zasobów,",
        "brak elementów oceniania, testy generatora oraz testy wznowienia nauki.",
        "Dla 20 pakietów wykonywanych jest łącznie 60 scenariuszy zakładek.",
        "",
    ]
    if number == 1:
        paragraphs.extend([
            "Uruchomienie wcześniejszej wersji RC4 zostało potwierdzone w Moodle PRz.",
            "Symulacja LMS potwierdziła ukończenie przy 100 procentach,",
            "brak ukończenia przy 99 procentach i brak ocen punktowych.",
            "Nie oznacza to certyfikacji LMS ani potwierdzenia zapisu ukończenia w Moodle.",
        ])
    else:
        paragraphs.extend([
            "Pakiet przeszedł automatyczne testy i jest gotowy do importu.",
            "Uruchomienia tego konkretnego pakietu w Moodle PRz nie potwierdzono.",
            "Testy symulowanego LMS nie stanowią certyfikacji środowiska produkcyjnego.",
        ])
    paragraphs.extend([
        "",
        "Źródło: " + source,
        "SHA-256: " + sha,
        "",
        "Oryginalny eksport Rise pozostaje niezmieniony.",
        "Nie należy usuwać istniejących prób i danych postępu studentów.",
    ])
    note = "\n".join(paragraphs) + "\n"
    if DISALLOWED.search(note):
        raise ValueError("Opis zawiera niedozwolony znak myślnika")
    return note

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads((args.build / "build-report.json").read_text(encoding="utf-8"))
    if len(report) != 20:
        raise ValueError(f"Oczekiwano 20 pakietów, otrzymano {len(report)}")
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for item in report:
        source = item["source"]
        number = int(source.split("-", 1)[0])
        if not 1 <= number <= 20:
            raise ValueError("Niepoprawny numer kursu")
        title = Path(source).stem.split("-", 1)[1].replace("-", " ").replace("_", " ")
        version = "2.0.0" if number == 1 else "1.0.0"
        tag = f"scorm{number:02d}-v{version}"
        filename = item["artifact"]
        path = args.build / filename
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if item["sha256"] != digest:
            raise ValueError(f"Niezgodna suma SHA-256 pakietu {number}")
        text = notes(number, title, version, source, digest)
        note_path = args.output / f"{tag}.md"
        note_path.write_text(text, encoding="utf-8")
        records.append({
            "number": number, "tag": tag, "version": version,
            "title": f"SCORM {number:02d}: {title}. Wersja {version}",
            "source": source, "artifact": filename,
            "notes": str(note_path), "sha256": digest,
        })
    records.sort(key=lambda item: item["number"])
    if [r["number"] for r in records] != list(range(1, 21)):
        raise ValueError("Brak pakietu lub powtarzający się numer")
    (args.output / "releases.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output / "SHA256SUMS.txt").write_text(
        "".join(f'{r["sha256"]}  {r["artifact"]}\n' for r in records),
        encoding="utf-8"
    )
    print("Przygotowano 20 opisów wydania, wszystkie bez niedozwolonych znaków.")

if __name__ == "__main__":
    main()

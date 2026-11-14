"""Release metadata validation for the twenty SCORM 1.2 packages."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prepare_scorm_releases.py"
spec = importlib.util.spec_from_file_location("prepare_scorm_releases", SCRIPT)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

class ReleaseMetadataTests(unittest.TestCase):
    def test_punctuation_and_evidence(self):
        for number in range(1, 21):
            version = "2.0.0" if number == 1 else "1.0.0"
            note = release.notes(number, "Podstawy algorytmów", version,
                                 f"{number}-source.zip", "a" * 64)
            self.assertIsNone(release.DISALLOWED.search(note))
            self.assertIn("SCORM 1.2", note)
            self.assertIn("SHA-256:", note)
            self.assertIn("zapisanych danych postępu", note)
            if number == 1:
                self.assertIn("RC4", note)
            else:
                self.assertIn("nie potwierdzono", note)

    def test_reject_nonstandard_dash(self):
        self.assertIsNotNone(release.DISALLOWED.search("niepoprawny — opis"))
        self.assertIsNotNone(release.DISALLOWED.search("niepoprawny – opis"))
        self.assertIsNone(release.DISALLOWED.search("tekst po polsku, bez pauzy"))

if __name__ == "__main__":
    unittest.main()

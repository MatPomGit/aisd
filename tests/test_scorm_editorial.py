"""Regression tests for the first narrative edition of SCORM 01."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scorm_pipeline as scorm
from scorm_editorial import EditorialError, SCORM01_COURSE_ID, apply_editorial

SOURCE = ROOT / "raw" / "1-podstawy-algorytmów.zip"


class EditorialPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SOURCE.is_file():
            raise unittest.SkipTest("Canonical SCORM 01 original not available")
        with scorm.open_zip(SOURCE) as zf:
            _, _, _, cls.original = scorm.get_data(zf)
            cls.tracking = scorm.get_tracking(zf.read(scorm.HTML).decode("utf-8-sig"))

    def test_scorm01_overlay_rewrites_intro_with_trace_and_invariant(self):
        before = copy.deepcopy(self.original)
        updated, quiz = scorm.new_course(before, self.tracking)
        self.assertEqual(before, self.original)  # Source in memory is not mutated.
        self.assertEqual(updated["course"]["id"], SCORM01_COURSE_ID)
        self.assertIsNotNone(quiz)
        intro = updated["course"]["lessons"][0]
        self.assertEqual(intro["title"], "Wprowadzenie do algorytmów")
        self.assertEqual(len(intro["items"]), 10)
        self.assertEqual(intro["items"][1]["items"][0]["heading"],
                         "Milion rekordów. Od czego zacząć?")
        text = str(intro["items"])
        for phrase in ("ZWRÓĆ -1", "niezmiennik pętli", "O(n)", "O(1)",
                       "Pusta tablica", "Powtarzające się wartości"):
            self.assertIn(phrase, text)
        self.assertNotIn("Jasne określenie celów", text)
        self.assertNotIn("Zrozumienie algorytmów to pierwszy krok", text)
        self.assertEqual(scorm.assessment_counts(updated),
                         {"quizzes": 0, "knowledge_checks": 0,
                          "assessment_headings": 0})

    def test_altering_known_rise_block_id_fails_closed(self):
        altered = copy.deepcopy(self.original)
        altered["course"]["lessons"][0]["items"][1]["id"] = "unknown-block-id"
        with self.assertRaises(scorm.BuildError) as cm:
            scorm.new_course(altered, self.tracking)
        self.assertIn("Editorial overlay rejected", str(cm.exception))

    def test_missing_expected_text_field_fails_closed(self):
        altered = copy.deepcopy(self.original)
        del altered["course"]["lessons"][0]["items"][1]["items"][0]["heading"]
        with self.assertRaises(scorm.BuildError):
            scorm.new_course(altered, self.tracking)

    def test_other_courses_do_not_receive_scorm01_overlay(self):
        example = {"course": {"id": "course-not-01", "lessons": []}}
        self.assertIsNone(apply_editorial(example))
        self.assertEqual(example["course"]["lessons"], [])

    def test_full_real_zip_build_validates_without_touching_source(self):
        before = SOURCE.stat().st_size
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "1-podstawy-algorytmów-bez-testow.zip"
            result = scorm.build_one(SOURCE, target)
            self.assertEqual(result["editorial_overlay"], "scorm01/lesson-01@1.0.0")
            self.assertEqual(result["lesson_count"], 11)
            self.assertEqual(scorm.validate_pair(SOURCE, target)["status"], "PASS")
            with scorm.open_zip(target) as zf:
                _, _, _, new_data = scorm.get_data(zf)
                intro = new_data["course"]["lessons"][0]
                self.assertEqual(intro["items"][1]["items"][0]["heading"],
                                 "Milion rekordów. Od czego zacząć?")
                self.assertEqual(scorm.get_tracking(
                    zf.read(scorm.HTML).decode("utf-8-sig")), scorm.TRACKING)
        self.assertEqual(SOURCE.stat().st_size, before)


if __name__ == "__main__":
    unittest.main()

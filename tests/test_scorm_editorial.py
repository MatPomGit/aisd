"""Scientific/editorial regression for six revised SCORM 01 lessons."""
import copy
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scorm_pipeline as scorm
from scorm_editorial import SCORM01_COURSE_ID, SCORM01_RELEASE, apply_editorial

SOURCE = ROOT / "raw" / "1-podstawy-algorytmów.zip"


def count_words(value):
    text = re.sub(r"<[^>]+>", " ", str(value))
    return len(re.findall(r"\b[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+\b", text))


class EditorialPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SOURCE.is_file():
            raise unittest.SkipTest("Canonical SCORM 01 source is unavailable")
        with scorm.open_zip(SOURCE) as zipfile:
            _, _, _, cls.original = scorm.get_data(zipfile)
            cls.tracking = scorm.get_tracking(
                zipfile.read(scorm.HTML).decode("utf-8-sig"))

    def prepared(self):
        original = copy.deepcopy(self.original)
        result, quiz = scorm.new_course(original, self.tracking)
        self.assertEqual(original, self.original, "Rebuilding mutated input")
        self.assertIsNotNone(quiz)
        return result

    def test_revisions_are_applied_to_six_specific_lessons(self):
        edited = self.prepared()
        lessons = edited["course"]["lessons"]
        self.assertEqual(edited["course"]["id"], SCORM01_COURSE_ID)
        self.assertEqual(len(lessons), 11)
        self.assertEqual([len(l["items"]) for l in lessons[:6]],
                         [10, 7, 7, 7, 5, 6])
        self.assertEqual([l["id"] for l in lessons],
                         [l["id"] for l in self.original["course"]["lessons"][:-1]])
        self.assertEqual(lessons[4]["title"],
                         "Rozmiar danych i tempo wzrostu kosztu")
        self.assertEqual(scorm.assessment_counts(edited),
                         {"quizzes": 0, "knowledge_checks": 0,
                          "assessment_headings": 0})

    def test_intro_has_explicit_loop_bounds_and_invariant(self):
        intro = str(self.prepared()["course"]["lessons"][0]["items"])
        for term in ("Milion rekordów", "DOPÓKI i &lt; n",
                     "i ← i + 1", "ZWRÓĆ -1", "niezmiennik pętli",
                     "O(n)", "O(1)", "Pusta tablica"):
            with self.subTest(term=term):
                self.assertIn(term, intro)
        self.assertNotIn("Jasne określenie celów", intro)

    def test_definitions_do_not_confuse_randomization_and_nondeterminism(self):
        lesson = str(self.prepared()["course"]["lessons"][1]["items"])
        for term in ("niedeterminizmem", "randomizowany",
                     "rekurencyjny", "aproksymacyjny", "dopuszczalne"):
            with self.subTest(term=term):
                self.assertIn(term, lesson)
        self.assertNotIn("W tej lekcji skupimy się", lesson)

    def test_pseudocode_and_python_have_same_first_occurrence_contract(self):
        lesson = str(self.prepared()["course"]["lessons"][2]["items"])
        for term in ("DOPÓKI i &lt; n", "i ← i + 1",
                     "enumerate(A)", "return -1", "== x"):
            with self.subTest(term=term):
                self.assertIn(term, lesson)
        def search_linear(values, needle):
            for index, value in enumerate(values):
                if value == needle:
                    return index
            return -1
        cases = [
            ([], 7, -1), ([7], 7, 0), ([3, 5, 7], 7, 2),
            ([31, 7, 42, 7], 7, 1), ([3, 5], 7, -1),
            ([-4, 0, -4], -4, 0),
        ]
        for a, x, expected in cases:
            with self.subTest(a=a, x=x):
                self.assertEqual(search_linear(a, x), expected)

    def test_complexity_states_average_case_assumptions(self):
        lessons = self.prepared()["course"]["lessons"]
        analysis = str(lessons[3]["items"])
        bounds = str(lessons[4]["items"])
        for phrase in ("(n + 1)/2", "jednostajnie", "niezmiennik",
                       "Poprawność częściowa", "Poprawność całkowita"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, analysis)
        self.assertIn("nie synonim", bounds)
        self.assertIn("O(f(n))", bounds)
        self.assertIn("Ω(f(n))", bounds)
        self.assertIn("Θ(f(n))", bounds)
        self.assertNotIn("jak szybko rośnie złożoność algorytmu w najgorszym przypadku",
                         bounds)


    def test_case_study_rejects_premature_stop_and_off_by_one(self):
        case = self.prepared()["course"]["lessons"][5]
        self.assertEqual(case["title"],
                         "Studium przypadku: poprawność przed optymalizacją")
        text = str(case["items"])
        for term in ("[8, 3, 7]", "A[i] &gt; x", "i &lt; n",
                     "nieposortowanych", "najmniejszym", "pięć",
                     "przypadku"):
            with self.subTest(term=term):
                self.assertIn(term.casefold(), text.casefold())
        process = next(b for b in case["items"] if b["variant"] == "process")
        self.assertEqual(len(process["items"]), 5)
        self.assertTrue(all("description" in row and "title" in row
                            for row in process["items"]))

    def test_no_redundant_boilerplate_and_shorter_six_lessons(self):
        edited = self.prepared()
        before = sum(count_words(l["items"]) for l in
                     self.original["course"]["lessons"][:6])
        after = sum(count_words(l["items"]) for l in
                    edited["course"]["lessons"][:6])
        self.assertLess(after, before * 0.85,
                        f"Redaction did not reduce redundancy: {before}, {after}")
        for lesson in edited["course"]["lessons"][:6]:
            content = str(lesson["items"])
            self.assertNotIn("Cele lekcji pomagają określić", content)
            self.assertNotIn("Zanim przejdziesz dalej, sprawdź", content)

    def test_changes_to_known_block_ids_fail_closed(self):
        for index in range(6):
            original = copy.deepcopy(self.original)
            original["course"]["lessons"][index]["items"][0]["id"] = "unknown-id"
            with self.subTest(lesson=index + 1):
                with self.assertRaisesRegex(scorm.BuildError,
                                            "Editorial overlay rejected"):
                    scorm.new_course(original, self.tracking)

    def test_missing_required_rise_field_fails_closed(self):
        original = copy.deepcopy(self.original)
        del original["course"]["lessons"][1]["items"][1]["items"][0]["heading"]
        with self.assertRaises(scorm.BuildError):
            scorm.new_course(original, self.tracking)

    def test_other_courses_remain_unaffected(self):
        other = {"course": {"id": "different-course", "lessons": []}}
        self.assertIsNone(apply_editorial(other))
        self.assertEqual(other["course"]["lessons"], [])

    def test_full_zip_roundtrip_preserves_manifest_and_runtime(self):
        before = SOURCE.stat().st_size
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "1-podstawy-algorytmów-bez-testow.zip"
            report = scorm.build_one(SOURCE, output)
            self.assertEqual(report["editorial_overlay"], SCORM01_RELEASE)
            self.assertEqual(report["lesson_count"], 11)
            self.assertEqual(scorm.validate_pair(SOURCE, output)["status"], "PASS")
            with scorm.open_zip(output) as source:
                _, _, _, edited = scorm.get_data(source)
                self.assertEqual(len(edited["course"]["lessons"][5]["items"]), 6)
                self.assertEqual(scorm.get_tracking(
                    source.read(scorm.HTML).decode("utf-8-sig")), scorm.TRACKING)
        self.assertEqual(SOURCE.stat().st_size, before)


if __name__ == "__main__":
    unittest.main()

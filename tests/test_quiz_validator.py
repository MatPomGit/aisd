"""Regresja walidatora GIFT: wyłącznie jednokrotny wybór."""
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_quizzes as validator

ROOT = Path(__file__).resolve().parents[1]


class QuizValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "quiz_w03.gift"
        self.original = (ROOT / "quizzes" / "quiz_w03.gift").read_text(encoding="utf-8")
        self.path.write_text(self.original, encoding="utf-8")

    def check(self, content):
        self.path.write_text(content, encoding="utf-8")
        return validator.inspect_file(self.path, 3)

    def test_valid_single_choice_bank(self):
        self.assertEqual(self.check(self.original), [])

    def test_all_options_have_feedback(self):
        for index in range(1, 21):
            filename = ROOT / "quizzes" / f"quiz_w{index:02d}.gift"
            content = filename.read_text(encoding="utf-8")
            self.assertEqual(content.count("  ####"), 20)
            self.assertEqual(
                sum(
                    1 for line in content.splitlines()
                    if line.startswith(("  =", "  ~"))
                    and validator.split_gift_feedback(line)[1] is not None
                ),
                80,
            )

    def test_missing_answer_feedback(self):
        original_line = next(
            line for line in self.original.splitlines()
            if line.startswith("  ~")
        )
        value, feedback = validator.split_gift_feedback(original_line)
        self.assertIsNotNone(feedback)
        changed = self.original.replace(original_line, value, 1)
        self.assertTrue(any(
            "merytorycznej informacji zwrotnej" in error
            for error in self.check(changed)
        ))

    def test_too_short_answer_feedback(self):
        original_line = next(
            line for line in self.original.splitlines()
            if line.startswith("  ~")
        )
        value, feedback = validator.split_gift_feedback(original_line)
        changed = self.original.replace(original_line, value + "#Nie.", 1)
        self.assertTrue(any(
            "merytorycznej informacji zwrotnej" in error
            for error in self.check(changed)
        ))

    def test_unescaped_hash_in_answer_feedback(self):
        original_line = next(
            line for line in self.original.splitlines()
            if line.startswith("  ~")
        )
        changed = self.original.replace(
            original_line, original_line + "#niezamaskowany", 1
        )
        self.assertTrue(any(
            "niepoprzedzony ukośnikiem znak sterujący" in error
            for error in self.check(changed)
        ))

    def test_short_general_feedback(self):
        original_line = next(
            line for line in self.original.splitlines()
            if line.startswith("  ####")
        )
        changed = self.original.replace(original_line, "  ####Tak.", 1)
        self.assertTrue(any(
            "podsumowania poprawnych odpowiedzi" in error
            for error in self.check(changed)
        ))

    def test_escaped_hash_is_literal(self):
        self.assertEqual(
            validator.split_gift_feedback(r"Wariant \#1#Wyjaśnienie."),
            (r"Wariant \#1", "Wyjaśnienie."),
        )

    def test_400_questions_are_single_choice(self):
        for lecture in range(1, 21):
            path = ROOT / "quizzes" / f"quiz_w{lecture:02d}.gift"
            content = path.read_text(encoding="utf-8")
            chunks = content.splitlines()
            self.assertEqual(sum(line.startswith("::AISD-") for line in chunks), 20)
            self.assertFalse(any(
                "Zaznacz wszystkie poprawne odpowiedzi" in line
                for line in chunks if line.startswith("::AISD-")
            ))
            keys = [0, 0, 0, 0]
            for chunk in content.split("::AISD-")[1:]:
                choices = [line for line in chunk.splitlines()
                           if line.startswith(("  =", "  ~"))]
                self.assertEqual(len(choices), 4)
                self.assertFalse(any(
                    line.startswith("  ~%") or line.startswith("  =%")
                    for line in choices
                ))
                correct = [i for i, line in enumerate(choices)
                           if line.startswith("  =")]
                self.assertEqual(len(correct), 1)
                keys[correct[0]] += 1
            self.assertEqual(keys, [5, 5, 5, 5])

    def test_multiselect_instruction_is_rejected(self):
        changed = self.original.replace(
            " {", " Zaznacz wszystkie poprawne odpowiedzi. {", 1,
        )
        self.assertTrue(any(
            "niedozwolone polecenie wielokrotnego wyboru" in error
            for error in self.check(changed)
        ))

    def test_weighted_positive_answer_is_rejected(self):
        original_line = next(
            line for line in self.original.splitlines()
            if line.startswith("  =")
        )
        changed = self.original.replace(
            original_line, original_line.replace("  =", "  ~%100%", 1), 1,
        )
        self.assertTrue(any(
            "niedozwolone wagi procentowe" in error
            for error in self.check(changed)
        ))

    def test_weighted_negative_answer_is_rejected(self):
        original_line = next(
            line for line in self.original.splitlines()
            if line.startswith("  ~")
        )
        changed = self.original.replace(
            original_line, original_line.replace("  ~", "  ~%-50%", 1), 1,
        )
        self.assertTrue(any(
            "niedozwolone wagi procentowe" in error
            for error in self.check(changed)
        ))

    def test_two_correct_answers_are_rejected(self):
        original_line = next(
            line for line in self.original.splitlines()
            if line.startswith("  ~")
        )
        changed = self.original.replace(
            original_line, original_line.replace("  ~", "  =", 1), 1,
        )
        self.assertTrue(any(
            "dokładnie jedną poprawną odpowiedź" in error
            for error in self.check(changed)
        ))


if __name__ == "__main__":
    unittest.main()

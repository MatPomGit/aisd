"""Regresja walidatora GIFT: jedno- i wielokrotny wybór."""
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

    def test_valid_mixed_bank(self):
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

    def test_missing_multiselect_instruction(self):
        altered = self.original.replace(
            "Zaznacz wszystkie poprawne odpowiedzi.",
            "Wybierz odpowiedź.",
            1,
        )
        self.assertTrue(any("brak jawnego polecenia" in x for x in self.check(altered)))

    def test_invalid_weight_sum(self):
        altered = self.original.replace("~%50%i < n+1", "~%40%i < n+1", 1)
        self.assertNotEqual(altered, self.original)
        self.assertTrue(any("niepoprawne wagi" in x for x in self.check(altered)))

    def test_invalid_negative_score(self):
        altered = self.original.replace("~%-50%i < n", "~%50%i < n", 1)
        self.assertNotEqual(altered, self.original)
        self.assertTrue(any("niepoprawne wagi" in x for x in self.check(altered)))

    def test_mixed_format_not_allowed(self):
        altered = self.original.replace("~%50%i <\= n", "=i <\= n", 1)
        self.assertNotEqual(altered, self.original)
        self.assertTrue(any("niepoprawne wagi" in x for x in self.check(altered)))


if __name__ == "__main__":
    unittest.main()

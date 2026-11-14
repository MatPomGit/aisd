"""Scientific/editorial regression for all eleven revised SCORM 01 lessons."""
import ast
import copy
import html
import json
import itertools
import subprocess
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

    def test_revisions_are_applied_to_all_eleven_lessons(self):
        edited = self.prepared()
        lessons = edited["course"]["lessons"]
        self.assertEqual(edited["course"]["id"], SCORM01_COURSE_ID)
        self.assertEqual(len(lessons), 11)
        self.assertEqual([len(l["items"]) for l in lessons],
                         [10, 7, 7, 7, 5, 6, 5, 4, 4, 6, 3])
        self.assertEqual([l["id"] for l in lessons],
                         [l["id"] for l in self.original["course"]["lessons"][:-1]])
        self.assertEqual(lessons[4]["title"],
                         "Rozmiar danych i tempo wzrostu kosztu")
        self.assertEqual(scorm.assessment_counts(edited),
                         {"quizzes": 0, "knowledge_checks": 0,
                          "assessment_headings": 0})

    def test_selected_ui_labels_are_polish_and_not_in_source_or_public_variant(self):
        candidate = self.prepared()["labelSet"]["labels"]
        source = self.original["labelSet"]["labels"]
        rules = json.loads((ROOT / "editorial" / "scorm01" /
                            "labels-pl.json").read_text(encoding="utf-8"))
        self.assertEqual(rules["scope"], "reviewed_visible_scorm01_labels_only")
        self.assertGreaterEqual(len(rules["replacements"]), 40)
        for key, rule in rules["replacements"].items():
            with self.subTest(key=key):
                self.assertEqual(source[key], rule["expected"])
                self.assertEqual(candidate[key], rule["replace"])
        unapproved, _ = scorm.new_course(
            self.original, self.tracking, include_editorial=False)
        self.assertEqual(unapproved["labelSet"]["labels"], source)
        self.assertEqual(self.prepared()["labelSet"]["iso639Code"], "pl")
        self.assertIsNone(self.prepared()["course"]["locale"])
        self.assertIsNone(self.prepared()["course"]["defaultLocaleId"])

    def test_changed_label_in_source_refuses_unreviewed_translation(self):
        source = copy.deepcopy(self.original)
        source["labelSet"]["labels"]["courseExit"] = "New vendor wording"
        with self.assertRaisesRegex(scorm.BuildError, "Source Rise label changed"):
            scorm.new_course(source, self.tracking)

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

    @staticmethod
    def execute_published_python(code, cases):
        """Parse the actual Rise Python listing and execute in a separate interpreter."""
        tree = ast.parse(code)
        allowed = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.For,
                   ast.If, ast.Compare, ast.Name, ast.Load, ast.Store, ast.Call,
                   ast.Eq, ast.Return, ast.Constant, ast.Tuple, ast.UnaryOp,
                   ast.USub)
        assert all(isinstance(node, allowed) for node in ast.walk(tree)), (
            "Unsupported constructs in the published code")
        assert len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef)
        fn = tree.body[0]
        assert fn.name == "pierwsze" and [arg.arg for arg in fn.args.args] == ["A", "x"]
        assert not fn.decorator_list and not fn.args.defaults
        assert all(isinstance(call.func, ast.Name) and
                   call.func.id == "enumerate" and len(call.args) == 1 and
                   not call.keywords for call in ast.walk(tree)
                   if isinstance(call, ast.Call))
        harness = (
            "import json, sys\n" + code +
            "\ncases = json.load(sys.stdin)\n"
            "print(json.dumps([pierwsze(a, x) for a, x in cases]))\n"
        )
        child = subprocess.run(
            [sys.executable, "-I", "-S", "-c", harness],
            input=json.dumps(cases), capture_output=True, text=True,
            timeout=4, check=True,
        )
        return json.loads(child.stdout)

    def test_pseudocode_and_python_have_same_first_occurrence_contract(self):
        lesson = self.prepared()["course"]["lessons"][2]
        text = str(lesson["items"])
        for term in ("DOPÓKI i &lt; n", "i ← i + 1",
                     "enumerate(A)", "return -1", "== x"):
            with self.subTest(term=term):
                self.assertIn(term, text)
        tabs = next(block for block in lesson["items"]
                    if block.get("variant") == "tabs")
        raw_html = tabs["items"][1]["description"]
        first_paragraph = re.search(r"<p>(.*?)</p>", raw_html, flags=re.DOTALL)
        self.assertIsNotNone(first_paragraph, "Published Python listing missing")
        lines = re.findall(r"<code>(.*?)</code>", first_paragraph.group(1))
        code = "\n".join(html.unescape(line).replace("\xa0", " ")
                         for line in lines)
        cases = [
            ([], 7), ([7], 7), ([3, 5, 7], 7),
            ([31, 7, 42, 7], 7), ([3, 5], 7),
            ([-4, 0, -4], -4),
        ]
        expected = [-1, 0, 2, 1, -1, 0]
        self.assertEqual(self.execute_published_python(code, cases), expected)
        # Exhaustive small-state verification against an independent oracle.
        alphabet = (-1, 0, 1)
        exhaustive = [
            (list(values), sought)
            for length in range(7)
            for values in itertools.product(alphabet, repeat=length)
            for sought in alphabet
        ]
        expected_exhaustive = [
            next((i for i, value in enumerate(values) if value == sought), -1)
            for values, sought in exhaustive
        ]
        self.assertEqual(
            self.execute_published_python(code, exhaustive), expected_exhaustive,
            "Published Python implementation differs from exhaustive first-match oracle"
        )
        # A deliberately broken return must not receive a false-positive PASS.
        mutated = code.replace("return i", "return -1")
        self.assertNotEqual(self.execute_published_python(mutated, cases),
                            expected)

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

    def test_rise_process_cards_follow_display_order_not_raw_row_order(self):
        """Rise stores its summary at row 1 but displays it last."""
        lessons = self.prepared()["course"]["lessons"]
        for lesson_index, count in ((5, 5), (7, 7)):
            with self.subTest(lesson=lesson_index + 1):
                process = next(b for b in lessons[lesson_index]["items"]
                               if b.get("variant") == "process")
                rows = process["items"]
                self.assertEqual([r.get("type") for r in rows],
                                 ["intro", "summary"] + ["step"] * (count - 2))
                display_order = [rows[0]] + rows[2:] + [rows[1]]
                self.assertEqual(
                    [int(r["title"].split(".", 1)[0]) for r in display_order],
                    list(range(1, count + 1)))
        # If the source schema changes, the editorial mapping must be reviewed.
        original = copy.deepcopy(self.original)
        process = next(b for b in original["course"]["lessons"][7]["items"]
                       if b.get("variant") == "process")
        process["items"][1]["type"] = "step"
        with self.assertRaisesRegex(scorm.BuildError, "Rise process intro/summary"):
            scorm.new_course(original, self.tracking)

    def test_no_redundant_boilerplate_and_shorter_full_course(self):
        edited = self.prepared()
        before = sum(count_words(l["items"]) for l in
                     self.original["course"]["lessons"][:-1])
        after = sum(count_words(l["items"]) for l in
                    edited["course"]["lessons"])
        self.assertLess(after, before * 0.85,
                        f"Redaction did not reduce redundancy: {before}, {after}")
        for lesson in edited["course"]["lessons"][:6]:
            content = str(lesson["items"])
            self.assertNotIn("Cele lekcji pomagają określić", content)
            self.assertNotIn("Zanim przejdziesz dalej, sprawdź", content)

    def test_changes_to_known_block_ids_fail_closed(self):
        for index in range(11):
            original = copy.deepcopy(self.original)
            original["course"]["lessons"][index]["items"][0]["id"] = "unknown-id"
            with self.subTest(lesson=index + 1):
                with self.assertRaisesRegex(scorm.BuildError,
                                            "Editorial overlay rejected"):
                    scorm.new_course(original, self.tracking)

    def test_changed_interactive_row_identity_or_order_fails_closed(self):
        for mutation in ("swap", "rename", "change_id"):
            original = copy.deepcopy(self.original)
            lesson = original["course"]["lessons"][2]
            block = next(b for b in lesson["items"]
                         if b["id"] == "cmi7guc35000z2a737n9m2s3a")
            rows = block["items"]
            if mutation == "swap":
                rows[0], rows[1] = rows[1], rows[0]
            elif mutation == "rename":
                rows[0]["title"] = "Changed original tab"
            else:
                rows[0]["id"] = "unexpected-entry-id"
            with self.subTest(mutation=mutation):
                with self.assertRaisesRegex(scorm.BuildError,
                                            "Interactive source row identity/order"):
                    scorm.new_course(original, self.tracking)

    def test_missing_required_rise_field_fails_closed(self):
        original = copy.deepcopy(self.original)
        del original["course"]["lessons"][1]["items"][1]["items"][0]["heading"]
        with self.assertRaises(scorm.BuildError):
            scorm.new_course(original, self.tracking)


    def test_unverified_ram_algorithms_are_removed(self):
        lessons = self.prepared()["course"]["lessons"]
        text = str(lessons[6:])
        for old in ("DIV 2", "MULT 2", "SUB 1", "READ 0",
                    "loop: JZERO end", "pętle porównujące i zamieniające"):
            with self.subTest(old=old):
                self.assertNotIn(old, text)
        self.assertIn("n(n − 1)/2", text)
        self.assertIn("O(n log n)", text)

    def test_ram_sum_program_runs_on_emulated_defined_semantics(self):
        """Execute actual instructions extracted from published Rise text."""
        lesson = self.prepared()["course"]["lessons"][8]
        tabs = next(b for b in lesson["items"] if b.get("variant") == "tabs")
        code = re.findall(r"<code>(.*?)</code>",
                          tabs["items"][1]["description"])
        start = code.index("LOAD =0")
        program = code[start:code.index("HALT", start) + 1]
        self.assertEqual(program, [
            "LOAD =0", "STORE 1", "loop: READ 2", "LOAD 2",
            "JZERO end", "ADD 1", "STORE 1", "JUMP loop",
            "end: WRITE 1", "HALT",
        ])
        lines, labels = [], {}
        for raw in program:
            label, sep, cmd = raw.partition(": ")
            if sep:
                labels[label] = len(lines)
            else:
                cmd = raw
            op, _, arg = cmd.partition(" ")
            lines.append((op, arg))

        def execute(input_values):
            regs = {}
            acc = pc = offset = 0
            output = []
            for _ in range(1000):
                op, arg = lines[pc]
                if op == "LOAD":
                    acc = int(arg[1:]) if arg.startswith("=") else regs[int(arg)]
                    pc += 1
                elif op == "STORE":
                    regs[int(arg)] = acc
                    pc += 1
                elif op == "READ":
                    if offset == len(input_values):
                        raise ValueError("Input ended without zero sentinel")
                    regs[int(arg)] = input_values[offset]
                    offset += 1
                    pc += 1
                elif op == "JZERO":
                    pc = labels[arg] if acc == 0 else pc + 1
                elif op == "ADD":
                    acc += regs[int(arg)]
                    pc += 1
                elif op == "JUMP":
                    pc = labels[arg]
                elif op == "WRITE":
                    output.append(regs[int(arg)])
                    pc += 1
                elif op == "HALT":
                    return output
                else:
                    self.fail("Unknown RAM instruction: " + op)
            self.fail("RAM program failed to halt within 1000 instructions")

        for inp, result in [
            ([0], 0), ([4, -2, 0], 2), ([4, -4, 0], 0),
            ([-5, 2, 0], -3), ([1, 2, 3, 0], 6),
            ([0, 1, 2], 0),
        ]:
            with self.subTest(inp=inp):
                self.assertEqual(execute(inp), [result])
        # Exhaustively cover negative values, internal zero sums, sentinel
        # termination and values trailing the first sentinel. This checks the
        # actual extracted instructional listing, not a reconstructed algorithm.
        for length in range(5):
            for prefix in itertools.product((-2, -1, 1, 2), repeat=length):
                for suffix in ((), (7, -9)):
                    case = [*prefix, 0, *suffix]
                    with self.subTest(case=case):
                        self.assertEqual(execute(case), [sum(prefix)])
        with self.assertRaises(ValueError):
            execute([5])

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
                self.assertEqual(len(edited["course"]["lessons"][10]["items"]), 3)
                html_content = source.read(scorm.HTML).decode("utf-8-sig")
                self.assertIn('<html lang="pl"', html_content)
                self.assertNotIn('<html lang="en"', html_content)
                self.assertEqual(scorm.get_tracking(html_content), scorm.TRACKING)
        self.assertEqual(SOURCE.stat().st_size, before)


if __name__ == "__main__":
    unittest.main()

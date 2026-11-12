"""Unit/integration tests for safe Rise 360 SCORM transformation."""
import base64
import copy
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scorm_pipeline as scorm


def sample(*, nonterminal=False, wrong_id=False, dangling=False, version="1.2"):
    quiz_id = "quiz-final"
    lesson = {"id": "lesson-1", "title": "Material", "type": "blocks", "items": []}
    quiz = {"id": quiz_id, "title": "Quiz", "type": "quiz",
            "items": [{"type": "multiple-choice", "question": "Q"}]}
    lessons = [quiz, lesson] if nonterminal else [lesson, quiz]
    data = {"course": {"lessons": lessons,
                       "exportSettings": {"quizId": quiz_id, "completeWith": "quiz",
                                          "quizComplete": True, "completionPercentage": 100,
                                          "reporting": "passed-incomplete"}}}
    if dangling:
        data["course"]["targetQuiz"] = quiz_id
    tracking_id = "wrong-id" if wrong_id else quiz_id
    encoded = base64.b64encode(json.dumps(data).encode()).decode()
    html = ('<html><script>async function __fetchCourse() {\n'
            'return Promise.resolve(deserialize("' + encoded + '"))\n'
            '}\n</script><script>\n'
            'var quizId = "' + tracking_id + '";\n'
            'var storylineId = null;\n'
            'var completionPercentage = 100;\n'
            "var reporting = 'passed-incomplete';\n"
            '</script></html>')
    manifest = ('<manifest xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2">'
                '<metadata><schema>ADL SCORM</schema><schemaversion>' + version
                + '</schemaversion></metadata>'
                '<resources><resource href="scormdriver/indexAPI.html">'
                '<file href="scormdriver/indexAPI.html"/>'
                '<file href="scormcontent/index.html"/>'
                '</resource></resources></manifest>')
    return {"imsmanifest.xml": manifest.encode(),
            "scormdriver/indexAPI.html": b"launch",
            "scormcontent/index.html": html.encode(),
            "scormcontent/assets/lesson.png": b"\x89PNGtest"}


def noquiz_fixture(*, embedded=False):
    """Fixture for an existing lesson-only Rise export."""
    files = sample()
    import re
    html = files["scormcontent/index.html"].decode()
    match = re.search(r'deserialize\("([A-Za-z0-9+/=]+)"\)', html)
    data = json.loads(base64.b64decode(match.group(1)))
    data["course"]["lessons"].pop()
    settings = data["course"]["exportSettings"]
    settings.update({"quizId": None, "completeWith": "reporting",
                     "quizComplete": False})
    if embedded:
        item_types = (["text", "text", "list", "divider"]
                      + ["knowledgeCheck"] * 7
                      + ["divider", "text", "interactive", "text", "interactive", "text"])
        first = data["course"]["lessons"][0]
        first["id"] = "cmiej97dl000d207092aujenc"
        first["title"] = "Test końcowy i omówienie rozwiązań"
        first["items"] = [{"id": str(i), "type": typ,
                            "variant": "tabs" if i == 13
                            else "accordion" if i == 15 else ""}
                           for i, typ in enumerate(item_types)]
    encoded = base64.b64encode(json.dumps(data).encode()).decode()
    html = html.replace(match.group(1), encoded, 1)
    html = html.replace('var quizId = "quiz-final";', "var quizId = null;")
    files["scormcontent/index.html"] = html.encode()
    return files


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.original = Path(self.tmp.name) / "raw.zip"
        self.output = Path(self.tmp.name) / "noquiz.zip"

    def write(self, files):
        with zipfile.ZipFile(self.original, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, data in files.items():
                zf.writestr(name, data)

    def test_build_removes_quiz_and_preserves_assets(self):
        self.write(sample())
        old = self.original.read_bytes()
        report = scorm.build_one(self.original, self.output)
        self.assertEqual(1, report["lesson_count"])
        self.assertEqual(old, self.original.read_bytes())
        self.assertEqual("PASS", scorm.validate_pair(self.original, self.output)["status"])
        with zipfile.ZipFile(self.output) as zf:
            _, _, _, data = scorm.get_data(zf)
            self.assertEqual(["lesson-1"], [l["id"] for l in data["course"]["lessons"]])
            self.assertEqual("course", data["course"]["exportSettings"]["completeWith"])
            self.assertEqual(scorm.TRACKING, scorm.get_tracking(
                zf.read("scormcontent/index.html").decode()))
            self.assertEqual(b"\x89PNGtest", zf.read("scormcontent/assets/lesson.png"))

    def test_existing_quiz_free_course_keeps_all_lessons(self):
        self.write(noquiz_fixture())
        report = scorm.build_one(self.original, self.output)
        self.assertIsNone(report["removed_quiz"])
        self.assertEqual(1, report["lesson_count"])
        self.assertFalse(report["embedded_test_removed"])
        self.assertEqual("PASS", scorm.validate_pair(self.original, self.output)["status"])

    def test_known_embedded_final_test_removed_without_losing_advice(self):
        self.write(noquiz_fixture(embedded=True))
        report = scorm.build_one(self.original, self.output)
        self.assertTrue(report["embedded_test_removed"])
        with zipfile.ZipFile(self.output) as zf:
            _, _, _, data = scorm.get_data(zf)
            last = data["course"]["lessons"][-1]
            self.assertEqual("Najczęstsze błędy i wskazówki", last["title"])
            self.assertEqual(["text", "interactive", "text"],
                             [x["type"] for x in last["items"]])
        self.assertEqual("PASS", scorm.validate_pair(self.original, self.output)["status"])

    def test_refuse_nonterminal_quiz(self):
        self.write(sample(nonterminal=True))
        with self.assertRaises(scorm.BuildError):
            scorm.build_one(self.original, self.output)
        self.assertFalse(self.output.exists())

    def test_refuse_mismatched_tracking(self):
        self.write(sample(wrong_id=True))
        with self.assertRaises(scorm.BuildError):
            scorm.build_one(self.original, self.output)

    def test_refuse_dangling_reference(self):
        self.write(sample(dangling=True))
        with self.assertRaises(scorm.BuildError):
            scorm.build_one(self.original, self.output)

    def test_refuse_scorm_2004(self):
        self.write(sample(version="2004 4th Edition"))
        with self.assertRaises(scorm.BuildError):
            scorm.build_one(self.original, self.output)

    def test_refuse_missing_manifest_resource(self):
        files = sample()
        del files["scormdriver/indexAPI.html"]
        self.write(files)
        with self.assertRaises(scorm.BuildError):
            scorm.build_one(self.original, self.output)

    def test_refuse_zip_traversal(self):
        files = sample()
        files["../escape"] = b"bad"
        self.write(files)
        with self.assertRaises(scorm.BuildError):
            scorm.build_one(self.original, self.output)

    def test_refuse_second_build_overwrite(self):
        self.write(sample())
        scorm.build_one(self.original, self.output)
        with self.assertRaises(scorm.BuildError):
            scorm.build_one(self.original, self.output)

    def test_refuse_tampered_output(self):
        self.write(sample())
        scorm.build_one(self.original, self.output)
        with zipfile.ZipFile(self.output, "a") as zf:
            zf.writestr("extra-file.txt", "malicious")
        with self.assertRaises(scorm.BuildError):
            scorm.validate_pair(self.original, self.output)


if __name__ == "__main__":
    unittest.main()

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

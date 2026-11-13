"""Guard discoverability of the mandatory SCORM lesson-review policy.

No ZIP or third-party package is needed: this checks repository documentation only.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs" / "lesson-review-and-rebuild.md"
TEMPLATE = ROOT / "docs" / "templates" / "lesson-review-template.md"


class EditorialPolicyDocsTests(unittest.TestCase):
    def test_required_documents_exist_and_are_linked_from_root_instructions(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(POLICY.is_file())
        self.assertTrue(TEMPLATE.is_file())
        self.assertIn("docs/lesson-review-and-rebuild.md", agents)
        self.assertIn("docs/templates/lesson-review-template.md", agents)
        self.assertIn("docs/scorm.md", agents)
        self.assertIn("wszystkie 20 pakietów", agents)

    def test_documentation_index_and_scorm_reference_policy(self):
        index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        scorm = (ROOT / "docs" / "scorm.md").read_text(encoding="utf-8")
        for name in ("lesson-review-and-rebuild.md",
                     "templates/lesson-review-template.md"):
            self.assertIn(name, index)
            self.assertIn(name, scorm)

    def test_policy_contains_all_review_and_release_gates(self):
        policy = POLICY.read_text(encoding="utf-8")
        for term in (
            "niezmiennik", "przypadki brzegowe", "poprawność",
            "złożoność", "narracja", "polszczyzn", "O(f(n))",
            "fail-closed", "Moodle", "SHA-256", "P0", "P1",
            "20 pakiet",
        ):
            with self.subTest(term=term):
                self.assertIn(term.casefold(), policy.casefold())
        self.assertRegex(policy, r"\*\*Wersja:\*\*\s*\d+\.\d+\.\d+")
        self.assertRegex(policy, r"## 7\. Kryteria akceptacji")

    def test_review_template_includes_evidence_and_decision(self):
        data = TEMPLATE.read_text(encoding="utf-8")
        for required in ("SHA-256", "Mierzalne efekty", "Przypadek",
                         "Kontrprzykład", "Decyzja końcowa", "Moodle",
                         "P0", "P1"):
            with self.subTest(required=required):
                self.assertIn(required.casefold(), data.casefold())

    def test_policy_links_resolve(self):
        targets = {
            ROOT / "AGENTS.md": [
                "docs/lesson-review-and-rebuild.md",
                "docs/templates/lesson-review-template.md",
                "docs/scorm.md",
            ],
            ROOT / "docs" / "README.md": [
                "lesson-review-and-rebuild.md",
                "templates/lesson-review-template.md",
            ],
            ROOT / "docs" / "scorm.md": [
                "lesson-review-and-rebuild.md",
                "templates/lesson-review-template.md",
            ],
            POLICY: ["templates/lesson-review-template.md"],
            TEMPLATE: ["../lesson-review-and-rebuild.md"],
        }
        for page, refs in targets.items():
            source = page.read_text(encoding="utf-8")
            for ref in refs:
                with self.subTest(page=page.name, ref=ref):
                    self.assertIn(f"]({ref})", source)
                    self.assertTrue((page.parent / ref).resolve().is_file())


if __name__ == "__main__":
    unittest.main()

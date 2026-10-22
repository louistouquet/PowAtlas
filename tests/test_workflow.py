import re
import unittest
from pathlib import Path

from powatlas.catalogue import load_catalogue

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "collect.yml"


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")
        _, self.tasks, self.settings = load_catalogue()

    def test_workflow_crons_match_catalogue(self):
        in_yaml = re.findall(r'^\s*- cron: "([^"]+)"', self.text, re.M)
        in_catalogue = [c for t in self.tasks.values() for c in t.crons]
        self.assertEqual(sorted(in_yaml), sorted(in_catalogue))

    def test_workflow_permissions_and_retention(self):
        for needle in ("actions: read", "issues: write", "contents: read", "concurrency:",
                       f"retention-days: {self.settings['artifact_retention_days']}", "workflow_dispatch:",
                       "if-no-files-found: error", "fail-fast: false"):
            self.assertIn(needle, self.text)

    def test_unit_level_concurrency(self):
        # Same unit never collected twice in parallel, even if two triggers overlap.
        self.assertIn("group: collect-unit-${{ matrix.unit }}", self.text)
        self.assertIn("--skip-if-complete", self.text)
        self.assertNotIn("github.event.schedule || inputs.task", self.text)

    def test_checkout_without_persisted_credentials(self):
        self.assertEqual(self.text.count("actions/checkout@v4"), self.text.count("persist-credentials: false"))

    def test_dispatch_inputs_validated(self):
        self.assertIn("^[a-z0-9-]+$", self.text)

    def test_no_expression_inside_run_scripts(self):
        # Inputs and matrix values reach shell scripts through env variables only.
        in_run = False
        for line in self.text.splitlines():
            stripped = line.strip()
            if stripped.startswith("run:"):
                in_run = True
                indent = len(line) - len(line.lstrip())
                self.assertNotIn("${{", stripped, line)
                continue
            if in_run:
                if stripped and len(line) - len(line.lstrip()) <= indent:
                    in_run = False
                else:
                    self.assertNotIn("${{", line, line)


if __name__ == "__main__":
    unittest.main()

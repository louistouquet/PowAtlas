import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from powatlas import adapters, cli
from powatlas.writer import Manifest


class FakeGitHub:
    def __init__(self, names, last_commit):
        self.names = names
        self.last_commit = last_commit
        self.issues = []

    def list_artifact_names(self):
        return list(self.names)

    def last_commit_date(self, branch):
        return self.last_commit

    def open_or_comment_issue(self, title, body, label):
        self.issues.append((title, body, label))


class FakeAdapter:
    def collect(self, unit, source, http, out_dir, mode, settings):
        return Manifest(unit="x", source=source.id, ref="r", state="partial", mode=mode, stream=None)


class CliCommandsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / "github_output"
        self.summary = self.tmp / "summary.md"
        self.env = mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(self.out), "GITHUB_STEP_SUMMARY": str(self.summary)})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_resolve_schedule(self):
        self.assertEqual(cli.main(["resolve-schedule", "--cron", "35 8 * * *"]), 0)
        self.assertEqual(self.out.read_text(), "task=icon-d2\nattempt=last\n")

    def test_plan_writes_units(self):
        gh = FakeGitHub([], datetime.now(timezone.utc))
        with mock.patch.object(cli, "make_github", return_value=gh):
            code = cli.main(["plan", "--task", "icon-d2", "--now", "2026-11-01T02:35:00Z"])
        self.assertEqual(code, 0)
        self.assertEqual(self.out.read_text(), 'units=["icon-d2__20261101T00Z"]\n')

    def test_collect_reports_state(self):
        old = dict(adapters.ADAPTERS)
        adapters.ADAPTERS["dwd-icon"] = FakeAdapter()
        try:
            code = cli.main(["collect", "--unit", "icon-d2__20261101T00Z", "--out", str(self.tmp / "o"),
                             "--now", "2026-11-01T02:35:00Z"])
        finally:
            adapters.ADAPTERS.clear()
            adapters.ADAPTERS.update(old)
        self.assertEqual(code, 0)
        self.assertEqual(self.out.read_text(), "state=partial\n")

    def test_collect_skips_already_complete_unit(self):
        gh = FakeGitHub(["icon-d2__20261101T00Z__complete"], datetime.now(timezone.utc))
        with mock.patch.object(cli, "make_github", return_value=gh):
            code = cli.main(["collect", "--unit", "icon-d2__20261101T00Z", "--out", str(self.tmp / "o"),
                             "--now", "2026-11-01T08:35:00Z", "--skip-if-complete"])
        self.assertEqual(code, 0)
        self.assertEqual(self.out.read_text(), "state=already-complete\n")

    def test_report_opens_issue_and_fails_on_loss(self):
        now = datetime(2026, 11, 1, 8, 35, tzinfo=timezone.utc)
        gh = FakeGitHub([], now - timedelta(days=1))
        with mock.patch.object(cli, "make_github", return_value=gh):
            code = cli.main(["report", "--task", "icon-d2", "--attempt", "last", "--now", "2026-11-01T08:35:00Z"])
        self.assertEqual(code, 1)
        self.assertEqual(gh.issues[0][0], "Collecte : pertes du 2026-11-01")
        self.assertEqual(gh.issues[0][2], "collecte")
        self.assertIn("icon-d2__20261101T00Z", self.summary.read_text())

    def test_report_green_on_first_attempt(self):
        gh = FakeGitHub([], datetime(2026, 10, 31, tzinfo=timezone.utc))
        with mock.patch.object(cli, "make_github", return_value=gh):
            code = cli.main(["report", "--task", "icon-d2", "--attempt", "first", "--now", "2026-11-01T02:35:00Z"])
        self.assertEqual((code, gh.issues), (0, []))


if __name__ == "__main__":
    unittest.main()

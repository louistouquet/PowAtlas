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

    def list_artifacts(self):
        return [{"name": n, "created_at": "2026-01-01T00:00:00Z"} for n in self.names]

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

    def test_plan_writes_units_and_plan_time(self):
        gh = FakeGitHub([], datetime.now(timezone.utc))
        with mock.patch.object(cli, "make_github", return_value=gh):
            code = cli.main(["plan", "--task", "icon-d2", "--now", "2026-11-01T02:35:00Z"])
        self.assertEqual(code, 0)
        # the plan time is passed to the report job, which may start much later
        self.assertEqual(self.out.read_text(), 'units=["icon-d2__20261101T00Z"]\nnow=2026-11-01T02:35:00Z\n')

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

    def test_token_read_from_env_file(self):
        env = self.tmp / ".env"
        env.write_text("# local secrets\nPOWATLAS_GITHUB_TOKEN='abc123'\nOTHER=x\n")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("POWATLAS_GITHUB_TOKEN", None)
            self.assertEqual(cli.pc_token(env), "abc123")
        with mock.patch.dict(os.environ, {"POWATLAS_GITHUB_TOKEN": "fromenv"}):
            self.assertEqual(cli.pc_token(env), "fromenv")

    def test_missing_token_is_an_error(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("POWATLAS_GITHUB_TOKEN", None)
            with self.assertRaises(SystemExit):
                cli.pc_token(self.tmp / "absent.env")

    def test_progress_prints_one_bar_per_backfill_source(self):
        import contextlib
        import io

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["progress", "--data", tempfile.mkdtemp()]), 0)
        lines = out.getvalue().splitlines()
        self.assertEqual([line.split()[0] for line in lines], ["aifs-single", "ifs-0p25", "gfs-0p25"])
        self.assertTrue(all(" 0 %" in line for line in lines))

    def test_backfill_dates_default_to_catalogue(self):
        args = cli.build_parser().parse_args(["backfill", "--source", "ifs-0p25", "--data", "d"])
        self.assertEqual((args.start, args.end), (None, None))

    def test_backfill_probe_urls(self):
        from powatlas.cli import probe_urls
        urls = probe_urls("ifs-0p25", "2025-01-10", steps=[0, 24])
        self.assertEqual(urls, ["https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/20250110/00z/ifs/0p25/oper/20250110000000-0h-oper-fc",
                                "https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/20250110/00z/ifs/0p25/oper/20250110000000-24h-oper-fc"])

    def run_quiet(self, argv):
        import contextlib
        import io

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(argv)
        return code, out.getvalue()

    def test_collect_pc_fails_when_a_unit_is_not_complete(self):
        from fakes import FakeHttp

        data = self.tmp / "data"
        with mock.patch.object(cli, "make_http", return_value=FakeHttp({})):
            code, out = self.run_quiet(["collect-pc", "--data", str(data), "--now", "2026-10-27T11:00:00Z"])
        self.assertEqual(code, 1)
        self.assertIn("arpa-piemonte__20261027: missing (new)", out)

    def test_collect_pc_green_when_complete(self):
        from fakes import FakeHttp

        arpa = "https://utility.arpa.piemonte.it/api_realtime/"
        http = FakeHttp({arpa + "pie_neve": b"[1]", arpa + "pie_anag": b"[2]"})
        with mock.patch.object(cli, "make_http", return_value=http):
            code, out = self.run_quiet(["collect-pc", "--data", str(self.tmp / "data"),
                                        "--now", "2026-10-27T11:00:00Z"])
        self.assertEqual((code, out), (0, "arpa-piemonte__20261027: complete (new)\n"))

    def test_store_files_copies_and_reports(self):
        from test_pc import copy_dir

        data = self.tmp / "data"
        copy_dir(data / "pc-collect")
        code, out = self.run_quiet(["store", "--from", str(data / "pc-collect"), "--data", str(data)])
        self.assertEqual((code, out), (0, "new 1, replaced 0, kept 0, rejected 0\n"))
        self.assertTrue((data / "observations" / "arpa-piemonte" / "2026" / "10" / "arpa-piemonte_20261027.json").exists())

    def test_store_fails_on_rejected_copy(self):
        from test_pc import copy_dir

        copy_dir(self.tmp / "copies", corrupt=True)
        code, out = self.run_quiet(["store", "--from", str(self.tmp / "copies"), "--data", str(self.tmp / "data")])
        self.assertEqual(code, 1)
        self.assertIn("rejected 1", out)

    def test_dates_of_each_file_of_an_archived_unit(self):
        import gzip

        from test_pc import copy_dir

        data = self.tmp / "data"
        copy_dir(data / "pc-collect", files={
            "arpa-piemonte_20261027T0745Z_pie-neve.json.gz": gzip.compress(b'[{"d": "2026-10-21"}, {"d": "2026-10-27"}]'),
            "arpa-piemonte_20261027T0745Z_pie-anag.json.gz": gzip.compress(b'[{"id": 1}]')})
        self.run_quiet(["store", "--from", str(data / "pc-collect"), "--data", str(data)])
        code, out = self.run_quiet(["dates", "--data", str(data), "--unit", "arpa-piemonte__20261027"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "arpa-piemonte_20261027T0745Z_pie-neve.json.gz: 2026-10-21 (1), 2026-10-27 (1)\n"
                              "arpa-piemonte_20261027T0745Z_pie-anag.json.gz: no date\n")

    def test_dates_of_absent_unit_is_an_error(self):
        code, out = self.run_quiet(["dates", "--data", str(self.tmp), "--unit", "arpa-piemonte__20261027"])
        self.assertEqual(code, 1)
        self.assertIn("not in the archive", out)

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

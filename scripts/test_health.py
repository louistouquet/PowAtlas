"""Tests for health.py (run: python3 -m unittest discover -s scripts -p 'test_*.py' -v)."""

import unittest
from datetime import datetime, timezone

import health

NOW = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)


def run(created, conclusion="success", event="workflow_dispatch", rid=1):
    return {"id": rid, "created_at": created, "conclusion": conclusion, "event": event, "status": "completed"}


def art(name, created="2026-10-25T10:00:00Z"):
    return {"name": name, "created_at": created, "expired": False}


class HealthTest(unittest.TestCase):
    def test_all_good(self):
        lines = health.health([run("2026-10-25T11:17:10Z")], [art("slf__20261025__complete")], [], NOW)
        self.assertEqual(lines, [])

    def test_failed_runs_listed(self):
        runs = [run("2026-10-25T11:17:10Z"), run("2026-10-24T19:51:53Z", "failure", "schedule", 7)]
        lines = health.health(runs, [], [], NOW)
        self.assertEqual(lines, ["failed collect run 2026-10-24T19:51:53Z (schedule): "
                                 "https://github.com/louistouquet/PowAtlas/actions/runs/7"])

    def test_old_failures_ignored(self):
        runs = [run("2026-10-25T11:17:10Z"), run("2026-10-22T19:51:53Z", "failure")]
        self.assertEqual(health.health(runs, [], [], NOW), [])

    def test_no_recent_success_flagged(self):
        lines = health.health([run("2026-10-25T08:17:10Z")], [], [], NOW)
        self.assertEqual(lines, ["last successful collect run 3.7 h ago (expected hourly, cron-job.org)"])

    def test_incomplete_units_use_best_state(self):
        arts = [art("arpa-piemonte__20261024__missing"), art("arpa-piemonte__20261024__missing"),
                art("icon-d2__20261025T00Z__partial"), art("icon-d2__20261025T00Z__complete")]
        lines = health.health([run("2026-10-25T11:17:10Z")], arts, [], NOW)
        self.assertEqual(lines, ["unit not complete (retried while within its window): "
                                 "arpa-piemonte__20261024 (missing)"])

    def test_open_collecte_issues_listed(self):
        issues = [{"number": 50, "title": "Collecte : pertes du 2026-10-24", "html_url": "https://x/50"}]
        lines = health.health([run("2026-10-25T11:17:10Z")], [], issues, NOW)
        self.assertEqual(lines, ["open issue 50: Collecte : pertes du 2026-10-24 (https://x/50)"])

    def test_render(self):
        self.assertEqual(health.render([]), "PowAtlas collection health: OK (GitHub side).")
        self.assertTrue(health.render(["x"]).startswith("PowAtlas collection health (tell the pilot"))


if __name__ == "__main__":
    unittest.main()

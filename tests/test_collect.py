import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from powatlas import adapters, collect
from powatlas.catalogue import Source, Task
from powatlas.writer import Manifest


def utc(*a):
    return datetime(*a, tzinfo=timezone.utc)


def source(id, window_days=0, family="fake"):
    return Source(id=id, family=family, kind="forecast", task="t1", fiche="docs/sources/icon-dwd.md",
                  licence="l", attribution="a", run_hours=(0,), steps=(0,), variables={"v": {}}, grid=None,
                  window_days=window_days, available_after_hours=1.0, urls={})


SOURCES = {"s1": source("s1"), "s2": source("s2", window_days=2), "other": source("other")}
SOURCES["other"] = Source(**{**SOURCES["other"].__dict__, "task": "t2"})


class FakeAdapter:
    def __init__(self):
        self.calls = []

    def collect(self, unit, source, http, out_dir, mode, settings):
        self.calls.append((unit, source.id, mode, out_dir))
        return Manifest(unit="u", source=source.id, ref="r", state="complete", mode=mode, stream=None)


class CollectTest(unittest.TestCase):
    def test_plan_returns_only_units_to_collect(self):
        now = utc(2026, 11, 3, 9)
        names = ["s2__20261102T00Z__complete", "s1__20261103T00Z__partial"]
        ids = collect.plan("t1", now, names, SOURCES)
        self.assertEqual(ids, ["s1__20261103T00Z", "s2__20261101T00Z", "s2__20261103T00Z"])

    def test_collect_unit_dispatches_by_family(self):
        fake = FakeAdapter()
        old = dict(adapters.ADAPTERS)
        adapters.ADAPTERS["fake"] = fake
        try:
            out = Path(tempfile.mkdtemp())
            m = collect.collect_unit("s2__20261101T00Z", out, http=None, sources=SOURCES, settings={},
                                     now=utc(2026, 11, 3, 9))
        finally:
            adapters.ADAPTERS.clear()
            adapters.ADAPTERS.update(old)
        self.assertEqual(m.state, "complete")
        unit, sid, mode, out_dir = fake.calls[0]
        self.assertEqual((sid, mode), ("s2", "catchup"))
        self.assertEqual(out_dir, out / "s2__20261101T00Z")

    def test_report_flags_losses_on_last_attempt(self):
        now = utc(2026, 11, 3, 15)
        losses, summary = collect.report("t1", now, "last", ["s1__20261103T00Z__complete"], now - timedelta(days=1), SOURCES)
        self.assertEqual(losses, ["s2__20261101T00Z"])
        self.assertIn("s2__20261101T00Z", summary)
        losses, _ = collect.report("t1", now, "first", [], now, SOURCES)
        self.assertEqual(losses, [])

    def test_auto_plans_every_scheduled_task(self):
        sources, tasks, _ = __import__("powatlas.catalogue", fromlist=["x"]).load_catalogue()
        now = utc(2026, 11, 1, 9, 55)
        ids = collect.plan("auto", now, [], sources, tasks)
        self.assertIn("icon-d2__20261101T00Z", ids)
        self.assertIn("ifs-0p25__20261101T00Z", ids)
        self.assertIn("slf__20261101", ids)
        self.assertFalse(any(i.startswith("gfs-0p25") for i in ids))  # PC-only source

    def test_auto_attempt_follows_second_trigger_time(self):
        from powatlas.catalogue import Task
        t = Task("icon-d2", ("35 2 * * *", "35 8 * * *"))
        self.assertEqual(collect.attempt_at(t, utc(2026, 11, 1, 8, 0)), "first")
        self.assertEqual(collect.attempt_at(t, utc(2026, 11, 1, 8, 35)), "last")
        self.assertEqual(collect.attempt_at(t, utc(2026, 11, 1, 9, 45)), "last")
        # later hourly runs do not report the same losses again
        self.assertEqual(collect.attempt_at(t, utc(2026, 11, 1, 9, 51)), "first")

    def test_recent_attempt_not_retried_within_three_hours(self):
        now = utc(2026, 11, 3, 9)
        artifacts = [{"name": "s1__20261103T00Z__partial", "created_at": "2026-11-03T07:30:00Z"},
                     {"name": "s2__20261102T00Z__missing", "created_at": "2026-11-03T05:00:00Z"}]
        recent = collect.recently_attempted(artifacts, now, hours=3)
        self.assertEqual(recent, {"s1__20261103T00Z"})
        ids = collect.plan("t1", now, [a["name"] for a in artifacts], SOURCES, skip=recent)
        self.assertNotIn("s1__20261103T00Z", ids)
        self.assertIn("s2__20261102T00Z", ids)

    def test_report_warns_after_45_days_without_commit(self):
        now = utc(2026, 12, 20, 15)
        _, summary = collect.report("t1", now, "first", [], now - timedelta(days=45), SOURCES)
        self.assertIn("Repository inactive for 45 days", summary)
        _, summary = collect.report("t1", now, "first", [], now - timedelta(days=44), SOURCES)
        self.assertNotIn("inactive", summary)


if __name__ == "__main__":
    unittest.main()

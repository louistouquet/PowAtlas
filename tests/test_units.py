import unittest
from datetime import datetime, timedelta, timezone

from powatlas.catalogue import Source
from powatlas.units import (
    Unit,
    artifact_name,
    best_states,
    definitive_losses,
    expected_units,
    parse_artifact_name,
    parse_unit_id,
    unit_id,
    units_to_collect,
)


def utc(*a):
    return datetime(*a, tzinfo=timezone.utc)


def source(id="icon-d2", kind="forecast", window_days=0, available_after_hours=1.5):
    return Source(
        id=id, family="x", kind=kind, task="t", fiche="docs/sources/icon-dwd.md", licence="l",
        attribution="a", run_hours=(0,), steps=(0, 1), variables={"v": {}}, grid=None,
        window_days=window_days, available_after_hours=available_after_hours, urls={},
    )


class NamesTest(unittest.TestCase):
    def test_artifact_name_round_trip(self):
        u = Unit("icon-d2", utc(2026, 11, 1, 0))
        name = artifact_name(u, "complete", "forecast")
        self.assertEqual(name, "icon-d2__20261101T00Z__complete")
        self.assertEqual(parse_artifact_name(name), (u, "complete"))
        o = Unit("slf", utc(2026, 11, 1))
        self.assertEqual(artifact_name(o, "partial", "observation"), "slf__20261101__partial")
        self.assertEqual(parse_artifact_name("slf__20261101__partial"), (o, "partial"))

    def test_foreign_artifact_names_ignored(self):
        self.assertIsNone(parse_artifact_name("coverage-report"))
        self.assertIsNone(parse_artifact_name("icon-d2__20261101T00Z__done"))

    def test_unit_id_round_trip(self):
        u = Unit("icon-eu", utc(2026, 11, 1, 0))
        self.assertEqual(unit_id(u, "forecast"), "icon-eu__20261101T00Z")
        self.assertEqual(parse_unit_id("icon-eu__20261101T00Z"), u)

    def test_naive_datetime_rejected(self):
        with self.assertRaises(ValueError):
            Unit("icon-d2", datetime(2026, 11, 1))

    def test_best_state_wins(self):
        names = ["a__20261101T00Z__partial", "a__20261101T00Z__complete", "a__20261102T00Z__missing"]
        best = best_states(names)
        self.assertEqual(best[Unit("a", utc(2026, 11, 1))], "complete")
        self.assertEqual(best[Unit("a", utc(2026, 11, 2))], "missing")


class PlanningTest(unittest.TestCase):
    def test_expected_units_respects_availability(self):
        s = source()
        self.assertEqual(expected_units(s, utc(2026, 11, 1, 1, 0)), [])
        self.assertEqual(expected_units(s, utc(2026, 11, 1, 2, 35)), [Unit("icon-d2", utc(2026, 11, 1, 0))])

    def test_window_covers_previous_days(self):
        s = source(id="arome", window_days=7, available_after_hours=6.0)
        units = expected_units(s, utc(2026, 11, 10, 6, 50))
        self.assertEqual(units[0].ref, utc(2026, 11, 3))
        self.assertEqual(units[-1].ref, utc(2026, 11, 10))
        self.assertEqual(len(units), 8)

    def test_observation_units_are_days(self):
        s = source(id="slf", kind="observation", available_after_hours=9.0)
        self.assertEqual(expected_units(s, utc(2026, 11, 1, 9, 50)), [Unit("slf", utc(2026, 11, 1))])

    def test_plan_skips_complete_units(self):
        s = source(id="arome", window_days=7, available_after_hours=6.0)
        now = utc(2026, 11, 10, 7)
        names = ["arome__20261109T00Z__complete", "arome__20261108T00Z__partial"]
        todo = units_to_collect(expected_units(s, now), names)
        refs = [u.ref for u in todo]
        self.assertNotIn(utc(2026, 11, 9), refs)
        self.assertIn(utc(2026, 11, 8), refs)
        self.assertEqual(len(todo), 7)

    def test_definitive_loss_on_last_attempt_only(self):
        s = source()
        now = utc(2026, 11, 1, 8, 35)
        self.assertEqual(definitive_losses(s, now, "first", []), [])
        self.assertEqual(definitive_losses(s, now, "last", []), [Unit("icon-d2", utc(2026, 11, 1))])
        self.assertEqual(definitive_losses(s, now, "last", ["icon-d2__20261101T00Z__complete"]), [])
        a = source(id="arome", window_days=7, available_after_hours=6.0)
        losses = definitive_losses(a, utc(2026, 11, 10, 12, 50), "last", [])
        self.assertEqual(losses, [Unit("arome", utc(2026, 11, 3))])

    def test_partial_counts_as_loss(self):
        s = source()
        now = utc(2026, 11, 1, 8, 35)
        self.assertEqual(len(definitive_losses(s, now, "last", ["icon-d2__20261101T00Z__partial"])), 1)


if __name__ == "__main__":
    unittest.main()

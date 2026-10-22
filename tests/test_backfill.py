import json
import unittest

from fakes import FakeHttp
from powatlas.backfill import probe


class ProbeTest(unittest.TestCase):
    def test_probe_counts_requests_and_bytes(self):
        index = "\n".join(json.dumps({"param": p, "levtype": "sfc", "step": "24", "_offset": i * 10, "_length": 10})
                          for i, p in enumerate(("tp", "2t", "sf"))).encode()
        http = FakeHttp({"https://aws/x-24h-oper-fc.index": index, "https://aws/x-24h-oper-fc.grib2": bytes(30)})
        r = probe(http, ["https://aws/x-24h-oper-fc"], ranges_per_url=2, clock=iter([0.0, 4.0]).__next__)
        self.assertEqual((r.requests, r.bytes, r.seconds), (3, len(index) + 20, 4.0))

    def test_probe_counts_slowdowns(self):
        class CountingHttp(FakeHttp):
            retry_count = 0

            def get(self, url, byte_range=None):
                self.retry_count += 2  # two SlowDown answers absorbed by retries
                return super().get(url, byte_range)

        index = json.dumps({"param": "tp", "levtype": "sfc", "step": "0", "_offset": 0, "_length": 5}).encode()
        http = CountingHttp({"https://aws/y.index": index, "https://aws/y.grib2": bytes(5)})
        r = probe(http, ["https://aws/y"], ranges_per_url=1, clock=iter([0.0, 1.0]).__next__)
        self.assertEqual(r.slowdowns, 4)


if __name__ == "__main__":
    unittest.main()


import json as _json
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

from powatlas import adapters
from powatlas.backfill import backfill, restrict_to_max_step
from powatlas.catalogue import load_catalogue
from powatlas.writer import Manifest

SOURCES, _, SETTINGS = load_catalogue()


class FakeAdapter:
    def __init__(self, state="complete"):
        self.calls = []
        self.state = state

    def collect(self, unit, source, http, out_dir, mode, settings):
        self.calls.append((unit.ref.date(), mode, max(source.steps)))
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{source.id}_{unit.ref:%Y%m%dT%HZ}"
        m = {"unit": f"{source.id}__{unit.ref:%Y%m%dT%HZ}", "source": source.id, "state": self.state, "files": []}
        (out_dir / f"{stem}.json").write_text(_json.dumps(m))
        return Manifest(unit=m["unit"], source=source.id, ref="r", state=self.state, mode=mode, stream=None)


class BackfillTest(unittest.TestCase):
    def run_backfill(self, start, end, fake, data=None, max_hours=None, clock=None):
        data = data or Path(tempfile.mkdtemp())
        old = dict(adapters.ADAPTERS)
        adapters.ADAPTERS["ecmwf"] = fake
        try:
            r = backfill(SOURCES["ifs-0p25"], start, end, data, http=None, settings=SETTINGS,
                         months=(11, 12, 1, 2, 3, 4), max_step=78, max_hours=max_hours,
                         clock=clock or (lambda: 0.0))
        finally:
            adapters.ADAPTERS.clear()
            adapters.ADAPTERS.update(old)
        return r, data

    def test_restrict_to_max_step(self):
        s = restrict_to_max_step(SOURCES["ifs-0p25"], 78)
        self.assertEqual(max(s.steps), 78)
        self.assertNotIn("mn2t6", s.variables)
        self.assertEqual(s.variables["mn2t3"]["steps"], [[3, 78, 3]])

    def test_backfill_months_filter(self):
        fake = FakeAdapter()
        r, _ = self.run_backfill(date(2024, 4, 29), date(2024, 5, 2), fake)
        self.assertEqual([c[0] for c in fake.calls], [date(2024, 4, 29), date(2024, 4, 30)])
        self.assertEqual({c[1:] for c in fake.calls}, {("backfill", 78)})
        self.assertEqual(r.done, 2)

    def test_backfill_skips_complete_units(self):
        fake = FakeAdapter()
        _, data = self.run_backfill(date(2025, 1, 1), date(2025, 1, 2), fake)
        again = FakeAdapter()
        r, _ = self.run_backfill(date(2025, 1, 1), date(2025, 1, 3), again, data=data)
        self.assertEqual(([c[0] for c in again.calls], r.skipped), ([date(2025, 1, 3)], 2))
        self.assertTrue((data / "forecasts/ifs-0p25/2025/01/ifs-0p25_20250101T00Z.json").is_file())

    def test_partial_units_are_retried(self):
        _, data = self.run_backfill(date(2025, 1, 1), date(2025, 1, 1), FakeAdapter("partial"))
        again = FakeAdapter()
        self.run_backfill(date(2025, 1, 1), date(2025, 1, 1), again, data=data)
        self.assertEqual(len(again.calls), 1)

    def test_partial_given_up_after_three_attempts(self):
        data = None
        for _ in range(3):
            _, data = self.run_backfill(date(2025, 1, 1), date(2025, 1, 1), FakeAdapter("partial"), data=data)
        again = FakeAdapter()
        r, _ = self.run_backfill(date(2025, 1, 1), date(2025, 1, 1), again, data=data)
        self.assertEqual((again.calls, r.given_up), ([], 1))

    def test_unreadable_manifest_recollected(self):
        data = Path(tempfile.mkdtemp())
        target = data / "forecasts/ifs-0p25/2025/01"
        target.mkdir(parents=True)
        (target / "ifs-0p25_20250101T00Z.json").write_text('{"unit": "ifs')
        fake = FakeAdapter()
        self.run_backfill(date(2025, 1, 1), date(2025, 1, 1), fake, data=data)
        self.assertEqual(len(fake.calls), 1)

    def test_complete_manifest_with_missing_file_recollected(self):
        data = Path(tempfile.mkdtemp())
        target = data / "forecasts/ifs-0p25/2025/01"
        target.mkdir(parents=True)
        (target / "ifs-0p25_20250101T00Z.json").write_text(_json.dumps(
            {"unit": "ifs-0p25__20250101T00Z", "state": "complete", "files": [{"name": "gone.nc", "sha256": "x"}]}))
        fake = FakeAdapter()
        self.run_backfill(date(2025, 1, 1), date(2025, 1, 1), fake, data=data)
        self.assertEqual(len(fake.calls), 1)

    def test_end_bounded_by_availability(self):
        from powatlas.backfill import last_available_day
        now = datetime(2026, 1, 10, 3, 0, tzinfo=timezone.utc)
        self.assertEqual(last_available_day(SOURCES["gfs-0p25"], now), date(2026, 1, 9))
        now = datetime(2026, 1, 10, 5, 0, tzinfo=timezone.utc)
        self.assertEqual(last_available_day(SOURCES["gfs-0p25"], now), date(2026, 1, 10))

    def test_backfill_stops_after_max_hours(self):
        ticks = iter([0.0, 0.0, 3600.0 * 2, 3600.0 * 3, 3600.0 * 4])
        fake = FakeAdapter()
        r, _ = self.run_backfill(date(2025, 1, 1), date(2025, 1, 10), fake, max_hours=1.5, clock=lambda: next(ticks))
        self.assertEqual((len(fake.calls), r.stopped), (1, True))

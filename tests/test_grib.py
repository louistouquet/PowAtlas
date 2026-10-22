import unittest
from datetime import datetime, timezone

import numpy as np

from gribfactory import make_message
from powatlas.grib import (
    GridMismatch,
    GridSpec,
    RefTimeMismatch,
    TruncatedMessage,
    check_grid,
    check_ref_time,
    crop_field,
    iter_fields,
)
from powatlas.domain import BBox

RUN = datetime(2026, 11, 1, 0, tzinfo=timezone.utc)


class IterFieldsTest(unittest.TestCase):
    def test_iter_fields_decodes_concatenated_messages(self):
        data = make_message("tp") + make_message("2t", step_range="24")
        fields = list(iter_fields(data))
        self.assertEqual([f.short_name for f in fields], ["tp", "2t"])
        for f in fields:
            self.assertEqual(f.ref_time, RUN)
            self.assertEqual(f.step_end, 24)
            self.assertEqual(f.values.dtype, np.float32)
            np.testing.assert_array_equal(f.values, np.arange(66).reshape(6, 11))

    def test_missing_values_become_nan(self):
        (f,) = iter_fields(make_message(missing_at=(2, 3)))
        self.assertTrue(np.isnan(f.values[2, 3]))
        self.assertEqual(int(np.isnan(f.values).sum()), 1)

    def test_lats_follow_scanning_order(self):
        (f,) = iter_fields(make_message(lat_first=47.0, dj=1.0))
        np.testing.assert_allclose(f.lats, [47, 46, 45, 44, 43, 42])
        (g,) = iter_fields(make_message(lat_first=42.0, dj=1.0, j_scans_positively=1))
        np.testing.assert_allclose(g.lats, [42, 43, 44, 45, 46, 47])
        np.testing.assert_allclose(f.lons, 4.0 + 0.5 * np.arange(11))

    def test_sub_hourly_step_decodes_in_minutes(self):
        # ICON-D2 files hold the hourly message plus three quarter-hour messages.
        data = make_message("tp", step_range="0-24") + make_message("tp", step_units="m", step_range="0-1455")
        hourly, quarter = iter_fields(data)
        self.assertEqual((hourly.step_end, hourly.step_end_minutes), (24, 1440))
        self.assertEqual((quarter.step_end, quarter.step_end_minutes), (None, 1455))

    def test_period_parameter_name_kept(self):
        # mn2t3 (3-hour minimum) must not be renamed by the switch to minute units.
        (f,) = iter_fields(make_message("mn2t3", step_range="0-3", type_of_level="heightAboveGround", level=2))
        self.assertEqual((f.short_name, f.step_end), ("mn2t3", 3))

    def test_keys_recorded(self):
        (f,) = iter_fields(make_message())
        self.assertIn("bitsPerValue", f.keys)
        self.assertEqual(f.keys["stepType"], "accum")
        self.assertEqual(f.keys["shortName"], "tp")

    def test_inconsistent_last_point_rejected(self):
        import eccodes
        h = eccodes.codes_new_from_message(make_message())
        eccodes.codes_set(h, "longitudeOfLastGridPointInDegrees", 9.5)
        bad = eccodes.codes_get_message(h)
        eccodes.codes_release(h)
        with self.assertRaises(ValueError):
            list(iter_fields(bad))

    def test_truncated_data_raises(self):
        with self.assertRaises(TruncatedMessage):
            list(iter_fields(make_message()[:-10]))
        with self.assertRaises(TruncatedMessage):
            list(iter_fields(b"<html>not found</html>"))


class ChecksTest(unittest.TestCase):
    def test_check_grid_detects_resolution_change(self):
        (f,) = iter_fields(make_message(di=0.5))
        check_grid(f, GridSpec(ni=11, nj=6, lat_first=47.0, lon_first=4.0, di=0.5, dj=1.0))
        with self.assertRaises(GridMismatch):
            check_grid(f, GridSpec(ni=11, nj=6, lat_first=47.0, lon_first=4.0, di=0.25, dj=1.0))

    def test_check_ref_time_rejects_previous_day(self):
        (f,) = iter_fields(make_message(date=20261031))
        with self.assertRaises(RefTimeMismatch):
            check_ref_time(f, RUN)
        (g,) = iter_fields(make_message())
        check_ref_time(g, RUN)


class CropFieldTest(unittest.TestCase):
    def test_crop_field_keeps_values_aligned(self):
        values = np.add.outer(10 * np.arange(6), np.arange(11)).astype(float)
        (f,) = iter_fields(make_message(values=values))
        c = crop_field(f, BBox(5.0, 44.0, 6.0, 45.0), margin_cells=0)
        np.testing.assert_allclose(c.lats, [45, 44])
        np.testing.assert_allclose(c.lons, [5.0, 5.5, 6.0])
        # lat 45 is row 2, lon 5.0 is column 2
        np.testing.assert_array_equal(c.values, [[22, 23, 24], [32, 33, 34]])


if __name__ == "__main__":
    unittest.main()

import unittest

import numpy as np

from powatlas.domain import ALPS, BBox, crop_points, crop_regular, normalize_lon


class CropRegularTest(unittest.TestCase):
    def test_global_quarter_degree_grid(self):
        lats = 90.0 - 0.25 * np.arange(721)  # north to south, as ECMWF and GFS
        lons = 0.25 * np.arange(1440)
        sj, si = crop_regular(lats, lons, ALPS, margin_cells=2)
        self.assertEqual((sj.start, sj.stop), (172, 189))  # 47.0 .. 43.0
        self.assertEqual((si.start, si.stop), (18, 34))  # 4.5 .. 8.25
        self.assertAlmostEqual(lats[sj][0], 47.0)
        self.assertAlmostEqual(lats[sj][-1], 43.0)
        self.assertAlmostEqual(lons[si][0], 4.5)
        self.assertAlmostEqual(lons[si][-1], 8.25)

    def test_icon_d2_grid_with_negative_longitudes(self):
        lats = 43.18 + 0.02 * np.arange(746)
        lons = 356.06 + 0.02 * np.arange(1215)  # first point 3.94 W, stored as 356.06 E
        sj, si = crop_regular(lats, lons, ALPS, margin_cells=2)
        clat = lats[sj]
        clon = normalize_lon(lons[si])
        self.assertTrue(np.all((clat >= 43.46 - 1e-9) & (clat <= 46.54 + 1e-9)))
        self.assertLessEqual(clat.min(), 43.5)
        self.assertGreaterEqual(clat.max(), 46.5)
        self.assertTrue(np.all((clon >= 4.96 - 1e-9) & (clon <= 7.94 + 1e-9)))
        self.assertLessEqual(clon.min(), 5.0)
        self.assertGreaterEqual(clon.max(), 7.9)

    def test_margin_clipped_at_grid_edge(self):
        lats = 43.52 + 0.02 * np.arange(200)
        lons = 4.0 + 0.02 * np.arange(300)
        sj, _ = crop_regular(lats, lons, ALPS, margin_cells=2)
        self.assertEqual(sj.start, 0)

    def test_bbox_outside_grid_raises(self):
        lats = 43.52 + 0.02 * np.arange(200)
        lons = 4.0 + 0.02 * np.arange(300)
        with self.assertRaises(ValueError):
            crop_regular(lats, lons, BBox(5.0, 43.0, 7.9, 46.5), margin_cells=2)

    def test_normalize_lon(self):
        np.testing.assert_allclose(normalize_lon(np.array([0.0, 179.9, 180.0, 356.06, -3.94])),
                                   [0.0, 179.9, -180.0, -3.94, -3.94])


class CropPointsTest(unittest.TestCase):
    def test_crop_points_keeps_margin(self):
        lons = np.array([5.0, 4.95, 4.8, 8.0])
        lats = np.array([43.5, 45.0, 45.0, 46.6])
        idx = crop_points(lats, lons, ALPS, margin_deg=0.1)
        self.assertEqual(idx.tolist(), [0, 1, 3])


if __name__ == "__main__":
    unittest.main()

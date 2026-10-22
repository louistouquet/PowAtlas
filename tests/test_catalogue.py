import unittest

from powatlas.catalogue import expand_steps, load_catalogue, task_for_cron


class CatalogueTest(unittest.TestCase):
    def setUp(self):
        self.sources, self.tasks, self.settings = load_catalogue()

    def test_steps_expand(self):
        steps = expand_steps([[0, 144, 3], [150, 360, 6]])
        self.assertEqual(len(steps), 85)
        self.assertEqual(steps[48], 144)
        self.assertEqual(steps[49], 150)
        self.assertEqual(steps[-1], 360)

    def test_overlapping_steps_rejected(self):
        with self.assertRaises(ValueError):
            expand_steps([[0, 12, 3], [12, 24, 6]])

    def test_task_for_cron(self):
        self.assertEqual(task_for_cron("35 8 * * *", self.tasks), ("icon-d2", "last"))
        self.assertEqual(task_for_cron("35 2 * * *", self.tasks), ("icon-d2", "first"))
        with self.assertRaises(KeyError):
            task_for_cron("0 0 * * *", self.tasks)

    def test_crons_unique_and_off_the_hour(self):
        crons = [c for t in self.tasks.values() for c in t.crons]
        self.assertEqual(len(crons), len(set(crons)))
        for c in crons:
            self.assertNotEqual(c.split()[0], "0", c)

    def test_icon_sources_declared(self):
        d2 = self.sources["icon-d2"]
        self.assertEqual(d2.family, "dwd-icon")
        self.assertEqual(d2.steps, tuple(range(49)))
        self.assertEqual(d2.grid.ni, 1215)
        self.assertEqual(set(d2.variables), {"t_2m", "tot_prec", "snow_gsp", "snow_con", "h_snow", "w_snow", "hzerocl", "snowlmt"})
        eu = self.sources["icon-eu"]
        self.assertEqual(len(eu.steps), 93)
        self.assertEqual(eu.steps[-1], 120)

    def test_every_fiche_exists(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        for s in self.sources.values():
            self.assertTrue((root / s.fiche).is_file(), s.fiche)

    def test_source_ids_validated(self):
        import tempfile
        from pathlib import Path
        text = (Path(__file__).resolve().parents[1] / "src/powatlas/catalogue.toml").read_text()
        bad = Path(tempfile.mkdtemp()) / "c.toml"
        bad.write_text(text.replace("[sources.icon-d2]", "[sources.ICON_d2]").replace("[sources.icon-d2.variables]", "[sources.ICON_d2.variables]"))
        with self.assertRaises(ValueError):
            load_catalogue(bad)

    def test_settings(self):
        self.assertEqual(self.settings["margin_cells"], 2)
        self.assertEqual(self.settings["bbox"], [5.0, 43.5, 7.9, 46.5])


if __name__ == "__main__":
    unittest.main()

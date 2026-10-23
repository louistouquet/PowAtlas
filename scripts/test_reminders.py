"""Tests for reminders.py (run: python3 -m unittest discover -s scripts -p 'test_*.py' -v)."""

import tempfile
import unittest
from datetime import date
from pathlib import Path

import reminders

CONF = {
    "pc": {"last_sync": date(2026, 10, 23), "warn_after_days": 20},
    "deadline": [
        {"what": "Renew token", "due": date(2027, 10, 22), "warn_days": 30},
    ],
    "waiting": [
        {"what": "Backfill AIFS: paste the done line", "since": date(2026, 10, 23)},
    ],
}


class RemindersTest(unittest.TestCase):
    def test_waiting_items_always_listed(self):
        lines = reminders.reminders(CONF, date(2026, 10, 24))
        self.assertEqual(lines, ["Waiting for the pilot since 2026-10-23 (1 days): Backfill AIFS: paste the done line"])

    def test_sync_reminder_after_threshold(self):
        lines = reminders.reminders({**CONF, "waiting": []}, date(2026, 11, 12))
        self.assertEqual(len(lines), 1)
        self.assertIn("last sync known 2026-10-23 (20 days ago", lines[0])

    def test_no_sync_reminder_before_threshold(self):
        self.assertEqual(reminders.reminders({**CONF, "waiting": []}, date(2026, 11, 11)), [])

    def test_deadline_warned_within_window_and_after(self):
        conf = {**CONF, "waiting": []}
        conf["pc"] = {**CONF["pc"], "last_sync": date(2027, 10, 15)}
        self.assertEqual(reminders.reminders(conf, date(2027, 9, 21)), [])
        self.assertEqual(reminders.reminders(conf, date(2027, 9, 22)), ["Due 2027-10-22 (in 30 days): Renew token"])
        self.assertEqual(reminders.reminders(conf, date(2027, 10, 23)), ["OVERDUE since 2027-10-22: Renew token"])

    def test_main_reads_file_and_prints_header(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "r.toml"
            path.write_text('[pc]\nlast_sync = 2026-10-23\nwarn_after_days = 20\n', encoding="utf-8")
            self.assertEqual(reminders.render(path, date(2026, 10, 24)), "PowAtlas reminders: nothing due.")
            path.write_text('[[waiting]]\nwhat = "X"\nsince = 2026-10-23\n', encoding="utf-8")
            text = reminders.render(path, date(2026, 10, 24))
            self.assertTrue(text.startswith("PowAtlas reminders (tell the pilot"))
            self.assertIn("- Waiting for the pilot", text)


    def test_project_file_is_valid(self):
        # docs/collecte/rappels.toml is edited by hand: every entry must carry its fields.
        text = reminders.render(reminders.DEFAULT_FILE, date(2026, 10, 24))
        self.assertTrue(text.startswith("PowAtlas reminders"))


if __name__ == "__main__":
    unittest.main()

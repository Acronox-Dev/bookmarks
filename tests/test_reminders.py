'''
Unit tests for the src.reminders module (reading reminder + reading time).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import unittest
from datetime import datetime, timedelta

from src import reminders
from src.config import DEFAULT_CONFIG


def make_bookmark(notes="Notes", last_read_date="2026-01-01 00:00:00"):
    """Build a minimal bookmark tuple with only the fields reminders.py reads."""
    return (1, "Title", "https://example.com", notes, last_read_date, last_read_date, 0, (), ())


class TestIsStale(unittest.TestCase):
    """Tests for reminders.is_stale."""

    def test_recently_read_bookmark_is_not_stale(self):
        recent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bookmark = make_bookmark(last_read_date=recent)
        self.assertFalse(reminders.is_stale(bookmark, DEFAULT_CONFIG))

    def test_old_bookmark_is_stale(self):
        old = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        bookmark = make_bookmark(last_read_date=old)
        self.assertTrue(reminders.is_stale(bookmark, DEFAULT_CONFIG))

    def test_respects_configured_threshold(self):
        just_over = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")
        bookmark = make_bookmark(last_read_date=just_over)
        config = {**DEFAULT_CONFIG, "reading_reminder_days": 7}
        self.assertTrue(reminders.is_stale(bookmark, config))


class TestEstimateReadingMinutes(unittest.TestCase):
    """Tests for reminders.estimate_reading_minutes."""

    def test_uses_default_words_when_notes_are_empty(self):
        bookmark = make_bookmark(notes="")
        config = {**DEFAULT_CONFIG, "default_reading_words": 200, "reading_speed_wpm": 200}
        self.assertEqual(reminders.estimate_reading_minutes(bookmark, config), 1)

    def test_scales_with_notes_word_count(self):
        bookmark = make_bookmark(notes=" ".join(["word"] * 400))
        config = {**DEFAULT_CONFIG, "reading_speed_wpm": 200}
        self.assertEqual(reminders.estimate_reading_minutes(bookmark, config), 2)

    def test_never_returns_less_than_one_minute(self):
        bookmark = make_bookmark(notes="one word")
        config = {**DEFAULT_CONFIG, "reading_speed_wpm": 1000}
        self.assertEqual(reminders.estimate_reading_minutes(bookmark, config), 1)


if __name__ == "__main__":
    unittest.main()

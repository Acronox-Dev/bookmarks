'''
Unit tests for the src.stats module (reading statistics).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import io
import unittest
from contextlib import redirect_stdout

from src import stats


def make_bookmark(bookmark_id, url="https://example.com", read_count=0,
                   last_read_date="2026-01-01 00:00:00", labels=()):
    """Build a bookmark tuple for tests, with sensible defaults."""
    return (
        bookmark_id, "Title", url, "Notes", "2026-01-01 00:00:00", last_read_date,
        read_count, labels, ()
    )


class TestComputeStats(unittest.TestCase):
    """Tests for stats.compute_stats."""

    def test_empty_list_returns_zeroed_stats(self):
        result = stats.compute_stats([])
        self.assertEqual(result["total_bookmarks"], 0)
        self.assertEqual(result["total_reads"], 0)
        self.assertIsNone(result["most_read"])

    def test_totals_and_average(self):
        bookmarks = [make_bookmark(1, read_count=3), make_bookmark(2, read_count=1)]
        result = stats.compute_stats(bookmarks)
        self.assertEqual(result["total_bookmarks"], 2)
        self.assertEqual(result["total_reads"], 4)
        self.assertEqual(result["avg_reads"], 2.0)

    def test_reads_by_domain(self):
        bookmarks = [
            make_bookmark(1, url="https://a.com", read_count=2),
            make_bookmark(2, url="https://a.com", read_count=3),
            make_bookmark(3, url="https://b.com", read_count=1)
        ]
        result = stats.compute_stats(bookmarks)
        self.assertEqual(result["reads_by_domain"], {"a.com": 5, "b.com": 1})

    def test_reads_by_label(self):
        bookmarks = [
            make_bookmark(1, read_count=2, labels=("work",)),
            make_bookmark(2, read_count=3, labels=("work", "urgent"))
        ]
        result = stats.compute_stats(bookmarks)
        self.assertEqual(result["reads_by_label"], {"work": 5, "urgent": 3})

    def test_most_read(self):
        bookmarks = [make_bookmark(1, read_count=1), make_bookmark(2, read_count=9)]
        result = stats.compute_stats(bookmarks)
        self.assertEqual(result["most_read"][0], 2)

    def test_least_recently_read(self):
        bookmarks = [
            make_bookmark(1, last_read_date="2026-06-01 00:00:00"),
            make_bookmark(2, last_read_date="2026-01-01 00:00:00")
        ]
        result = stats.compute_stats(bookmarks)
        self.assertEqual(result["least_recently_read"][0], 2)


class TestPrintStats(unittest.TestCase):
    """Tests for stats.print_stats."""

    def test_prints_a_message_when_there_are_no_bookmarks(self):
        output = io.StringIO()
        with redirect_stdout(output):
            stats.print_stats([])
        self.assertIn("No bookmarks", output.getvalue())

    def test_prints_totals(self):
        output = io.StringIO()
        with redirect_stdout(output):
            stats.print_stats([make_bookmark(1, read_count=2)])
        text = output.getvalue()
        self.assertIn("Total bookmarks: 1", text)
        self.assertIn("Total reads: 2", text)


if __name__ == "__main__":
    unittest.main()

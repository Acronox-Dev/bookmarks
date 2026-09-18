'''
Unit tests for the src.synthesis module (file synthesis / merging).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.
# pylint: disable=too-many-arguments,too-many-positional-arguments
# make_bookmark exposes every bookmark field as a keyword for readable tests.

import unittest

from src import synthesis


def make_bookmark(bookmark_id, title="Title", url="https://example.com", notes="Notes",
                   creation_date="2026-01-01 00:00:00", last_read_date="2026-01-01 00:00:00",
                   read_count=0, labels=()):
    """Build a bookmark tuple for tests, with sensible defaults."""
    return (
        bookmark_id, title, url, notes, creation_date, last_read_date, read_count, labels, ()
    )


class TestMergeDuplicate(unittest.TestCase):
    """Tests for synthesis.merge_duplicate."""

    def test_unions_labels(self):
        first = make_bookmark(1, labels=("work",))
        second = make_bookmark(2, labels=("urgent", "work"))
        merged = synthesis.merge_duplicate(first, second)
        self.assertEqual(merged[7], ("work", "urgent"))

    def test_keeps_the_higher_read_count(self):
        first = make_bookmark(1, read_count=2)
        second = make_bookmark(2, read_count=5)
        merged = synthesis.merge_duplicate(first, second)
        self.assertEqual(merged[6], 5)

    def test_keeps_the_most_recent_last_read_date(self):
        first = make_bookmark(1, last_read_date="2026-01-01 00:00:00")
        second = make_bookmark(2, last_read_date="2026-06-01 00:00:00")
        merged = synthesis.merge_duplicate(first, second)
        self.assertEqual(merged[5], "2026-06-01 00:00:00")

    def test_keeps_the_earliest_creation_date(self):
        first = make_bookmark(1, creation_date="2026-06-01 00:00:00")
        second = make_bookmark(2, creation_date="2026-01-01 00:00:00")
        merged = synthesis.merge_duplicate(first, second)
        self.assertEqual(merged[4], "2026-01-01 00:00:00")


class TestSynthesize(unittest.TestCase):
    """Tests for synthesis.synthesize."""

    def test_single_list_gets_renumbered_from_one(self):
        bookmarks = [
            make_bookmark(5, url="https://a.com"), make_bookmark(9, url="https://b.com")
        ]
        result = synthesis.synthesize([bookmarks])
        self.assertEqual([b[0] for b in result], [1, 2])

    def test_distinct_urls_across_files_are_all_kept(self):
        first = [make_bookmark(1, url="https://a.com")]
        second = [make_bookmark(1, url="https://b.com")]
        result = synthesis.synthesize([first, second])
        self.assertEqual(len(result), 2)
        self.assertEqual({b[2] for b in result}, {"https://a.com", "https://b.com"})

    def test_shared_url_across_files_is_merged(self):
        first = [make_bookmark(1, url="https://a.com", read_count=1)]
        second = [make_bookmark(1, url="https://a.com", read_count=9)]
        result = synthesis.synthesize([first, second])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][6], 9)

    def test_result_ids_are_sequential(self):
        first = [make_bookmark(1, url="https://a.com"), make_bookmark(2, url="https://b.com")]
        second = [make_bookmark(1, url="https://c.com")]
        result = synthesis.synthesize([first, second])
        self.assertEqual([b[0] for b in result], [1, 2, 3])

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(synthesis.synthesize([]), [])
        self.assertEqual(synthesis.synthesize([[], []]), [])


if __name__ == "__main__":
    unittest.main()

'''
Unit tests for the src.related module (reading sequence traversal).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import unittest

from src import related


def make_bookmark(bookmark_id, title="Title", related_ids=()):
    """Build a bookmark tuple for tests, with sensible defaults."""
    return (
        bookmark_id, title, "https://example.com", "Notes", "2026-01-01 00:00:00",
        "2026-01-01 00:00:00", 0, (), related_ids
    )


class TestReadingSequence(unittest.TestCase):
    """Tests for related.reading_sequence."""

    def test_unknown_start_id_returns_empty_list(self):
        bookmarks = [make_bookmark(1)]
        self.assertEqual(related.reading_sequence(bookmarks, 99), [])

    def test_bookmark_with_no_relations_returns_itself_only(self):
        bookmarks = [make_bookmark(1)]
        self.assertEqual(related.reading_sequence(bookmarks, 1), [bookmarks[0]])

    def test_follows_a_chain_of_relations(self):
        bookmarks = [
            make_bookmark(1, related_ids=(2,)),
            make_bookmark(2, related_ids=(1, 3)),
            make_bookmark(3, related_ids=(2,))
        ]
        result = related.reading_sequence(bookmarks, 1)
        self.assertEqual([b[0] for b in result], [1, 2, 3])

    def test_does_not_visit_a_bookmark_twice(self):
        bookmarks = [
            make_bookmark(1, related_ids=(2, 3)),
            make_bookmark(2, related_ids=(1, 3)),
            make_bookmark(3, related_ids=(1, 2))
        ]
        result = related.reading_sequence(bookmarks, 1)
        self.assertEqual(sorted(b[0] for b in result), [1, 2, 3])
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()

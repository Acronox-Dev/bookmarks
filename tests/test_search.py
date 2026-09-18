'''
Unit tests for the src.search module (search, filter, sort).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.
# pylint: disable=too-many-arguments,too-many-positional-arguments
# make_bookmark exposes every bookmark field as a keyword for readable tests.

import unittest

from src import search


def make_bookmark(bookmark_id, title="Title", url="https://example.com", notes="Notes",
                   creation_date="2026-01-01 00:00:00", last_read_date="2026-01-01 00:00:00",
                   read_count=0, labels=()):
    """Build a bookmark tuple for tests, with sensible defaults."""
    return (
        bookmark_id, title, url, notes, creation_date, last_read_date, read_count, labels, ()
    )


class TestDomainOf(unittest.TestCase):
    """Tests for search.domain_of."""

    def test_extracts_the_domain(self):
        bookmark = make_bookmark(1, url="https://example.com/path")
        self.assertEqual(search.domain_of(bookmark), "example.com")


class TestMatches(unittest.TestCase):
    """Tests for search.matches."""

    def test_query_matches_title_case_insensitively(self):
        bookmark = make_bookmark(1, title="Linux Archives")
        self.assertTrue(search.matches(bookmark, query="linux"))

    def test_query_matches_notes(self):
        bookmark = make_bookmark(1, notes="check every week")
        self.assertTrue(search.matches(bookmark, query="every"))

    def test_query_not_found_does_not_match(self):
        bookmark = make_bookmark(1, title="Title", notes="Notes")
        self.assertFalse(search.matches(bookmark, query="missing"))

    def test_label_filter_matches(self):
        bookmark = make_bookmark(1, labels=("work",))
        self.assertTrue(search.matches(bookmark, label="work"))

    def test_label_filter_no_match(self):
        bookmark = make_bookmark(1, labels=("work",))
        self.assertFalse(search.matches(bookmark, label="video"))

    def test_domain_filter_matches(self):
        bookmark = make_bookmark(1, url="https://example.com")
        self.assertTrue(search.matches(bookmark, domain="example.com"))

    def test_no_filters_always_matches(self):
        bookmark = make_bookmark(1)
        self.assertTrue(search.matches(bookmark))


class TestFilterBookmarks(unittest.TestCase):
    """Tests for search.filter_bookmarks."""

    def test_keeps_only_matching_bookmarks(self):
        bookmarks = [make_bookmark(1, labels=("work",)), make_bookmark(2, labels=("video",))]
        result = search.filter_bookmarks(bookmarks, label="work")
        self.assertEqual(result, [bookmarks[0]])


class TestSortBookmarks(unittest.TestCase):
    """Tests for search.sort_bookmarks."""

    def test_sorts_by_read_count_ascending(self):
        bookmarks = [make_bookmark(1, read_count=5), make_bookmark(2, read_count=1)]
        result = search.sort_bookmarks(bookmarks, sort_by="read_count")
        self.assertEqual([b[0] for b in result], [2, 1])

    def test_sorts_descending(self):
        bookmarks = [make_bookmark(1, read_count=1), make_bookmark(2, read_count=5)]
        result = search.sort_bookmarks(bookmarks, sort_by="read_count", descending=True)
        self.assertEqual([b[0] for b in result], [2, 1])

    def test_sorts_by_title_case_insensitively(self):
        bookmarks = [make_bookmark(1, title="banana"), make_bookmark(2, title="Apple")]
        result = search.sort_bookmarks(bookmarks, sort_by="title")
        self.assertEqual([b[0] for b in result], [2, 1])


if __name__ == "__main__":
    unittest.main()

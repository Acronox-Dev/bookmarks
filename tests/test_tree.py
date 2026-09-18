'''
Unit tests for the src.tree module (tree view grouping).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import io
import unittest
from contextlib import redirect_stdout

from src import tree
from src.config import DEFAULT_CONFIG


def make_bookmark(bookmark_id, url="https://example.com", labels=()):
    """Build a bookmark tuple for tests, with sensible defaults."""
    return (
        bookmark_id, "Title", url, "Notes", "2026-01-01 00:00:00",
        "2026-01-01 00:00:00", 0, labels, ()
    )


class TestGroupByCategory(unittest.TestCase):
    """Tests for tree.group_by_category."""

    def test_groups_labeled_bookmark_under_its_category(self):
        config = {**DEFAULT_CONFIG, "label_categories": {"work": "professional"}}
        bookmarks = [make_bookmark(1, labels=("work",))]
        result = tree.group_by_category(bookmarks, config)
        self.assertEqual(result["professional"]["professional"]["work"], bookmarks)

    def test_uncategorized_label_grouped_under_itself(self):
        bookmarks = [make_bookmark(1, labels=("work",))]
        result = tree.group_by_category(bookmarks, DEFAULT_CONFIG)
        self.assertEqual(result[tree.UNCATEGORIZED][tree.UNCATEGORIZED]["work"], bookmarks)

    def test_no_label_grouped_under_no_label(self):
        bookmarks = [make_bookmark(1)]
        result = tree.group_by_category(bookmarks, DEFAULT_CONFIG)
        self.assertEqual(
            result[tree.UNCATEGORIZED][tree.UNCATEGORIZED][tree.NO_LABEL], bookmarks
        )

    def test_nested_category_resolves_to_root(self):
        config = {
            **DEFAULT_CONFIG,
            "label_categories": {"urgent": "priority"},
            "category_parents": {"priority": "life"}
        }
        bookmarks = [make_bookmark(1, labels=("urgent",))]
        result = tree.group_by_category(bookmarks, config)
        self.assertEqual(result["life"]["priority"]["urgent"], bookmarks)


class TestGroupByDomain(unittest.TestCase):
    """Tests for tree.group_by_domain."""

    def test_groups_by_domain(self):
        bookmarks = [make_bookmark(1, url="https://a.com"), make_bookmark(2, url="https://b.com")]
        result = tree.group_by_domain(bookmarks)
        self.assertEqual(list(result["a.com"]), [bookmarks[0]])
        self.assertEqual(list(result["b.com"]), [bookmarks[1]])


class TestPrintTree(unittest.TestCase):
    """Tests for tree.print_tree."""

    def test_by_domain_prints_domains(self):
        bookmarks = [make_bookmark(1, url="https://a.com")]
        output = io.StringIO()
        with redirect_stdout(output):
            tree.print_tree(bookmarks, DEFAULT_CONFIG, by="domain")
        self.assertIn("a.com", output.getvalue())

    def test_by_category_prints_labels(self):
        bookmarks = [make_bookmark(1, labels=("work",))]
        output = io.StringIO()
        with redirect_stdout(output):
            tree.print_tree(bookmarks, DEFAULT_CONFIG, by="category")
        self.assertIn("work", output.getvalue())


if __name__ == "__main__":
    unittest.main()

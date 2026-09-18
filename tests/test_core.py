'''
Unit tests for the src.core module (in-memory bookmark operations).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.
# pylint: disable=too-many-arguments,too-many-positional-arguments
# make_bookmark exposes every bookmark field as a keyword for readable tests.

import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime

from src import core
from src.config import DEFAULT_CONFIG


def make_bookmark(bookmark_id, title="Title", url="https://example.com", notes="Notes",
                   creation_date="2026-01-01 00:00:00", last_read_date="2026-01-01 00:00:00",
                   read_count=0, labels=(), related_ids=()):
    """Build a bookmark tuple for tests, with sensible defaults."""
    return (
        bookmark_id, title, url, notes, creation_date, last_read_date, read_count,
        labels, related_ids
    )


class TestAdd(unittest.TestCase):
    """Tests for core.add."""

    def test_add_to_empty_list_uses_id_1(self):
        bookmark = core.add([], ("Title", "https://example.com", "Notes", ("work",)))
        self.assertEqual(bookmark[0], 1)
        self.assertEqual(bookmark[1:4], ("Title", "https://example.com", "Notes"))
        self.assertEqual(bookmark[6], 0)
        self.assertEqual(bookmark[7], ("work",))
        self.assertEqual(bookmark[8], ())

    def test_add_uses_next_available_id(self):
        bookmarks = [make_bookmark(1), make_bookmark(3)]
        bookmark = core.add(bookmarks, ("Title", "https://example.com", "Notes", ()))
        self.assertEqual(bookmark[0], 4)

    def test_add_sets_creation_and_last_read_date_equal(self):
        bookmark = core.add([], ("Title", "https://example.com", "Notes", ()))
        self.assertEqual(bookmark[4], bookmark[5])

    def test_add_does_not_mutate_input(self):
        bookmarks = [make_bookmark(1)]
        core.add(bookmarks, ("Title", "https://example.com", "Notes", ()))
        self.assertEqual(bookmarks, [make_bookmark(1)])


class TestFind(unittest.TestCase):
    """Tests for core.find."""

    def test_find_existing_bookmark(self):
        bookmarks = [make_bookmark(1), make_bookmark(2)]
        self.assertEqual(core.find(bookmarks, 2), make_bookmark(2))

    def test_find_missing_bookmark_returns_none(self):
        bookmarks = [make_bookmark(1)]
        self.assertIsNone(core.find(bookmarks, 99))

    def test_find_on_empty_list_returns_none(self):
        self.assertIsNone(core.find([], 1))


class TestModify(unittest.TestCase):
    """Tests for core.modify."""

    def test_modify_replaces_title_url_notes_labels(self):
        bookmarks = [make_bookmark(1, title="Old", url="https://old.com", notes="old")]
        updated = core.modify(bookmarks, 1, ("New", "https://new.com", "new", ("work",)))
        self.assertEqual(updated[0][1:4], ("New", "https://new.com", "new"))
        self.assertEqual(updated[0][7], ("work",))

    def test_modify_keeps_id_dates_and_related_ids(self):
        bookmarks = [make_bookmark(1, creation_date="2026-01-01 00:00:00",
                                    last_read_date="2026-01-02 00:00:00", read_count=5,
                                    related_ids=(2,))]
        updated = core.modify(bookmarks, 1, ("New", "https://new.com", "new", ()))
        self.assertEqual(updated[0][0], 1)
        self.assertEqual(updated[0][4], "2026-01-01 00:00:00")
        self.assertEqual(updated[0][5], "2026-01-02 00:00:00")
        self.assertEqual(updated[0][6], 5)
        self.assertEqual(updated[0][8], (2,))

    def test_modify_unknown_id_leaves_list_unchanged(self):
        bookmarks = [make_bookmark(1)]
        updated = core.modify(bookmarks, 99, ("New", "https://new.com", "new", ()))
        self.assertEqual(updated, bookmarks)

    def test_modify_only_updates_matching_bookmark(self):
        bookmarks = [make_bookmark(1), make_bookmark(2)]
        updated = core.modify(bookmarks, 1, ("New", "https://new.com", "new", ()))
        self.assertEqual(updated[1], make_bookmark(2))


class TestIncrementReadCount(unittest.TestCase):
    """Tests for core.increment_read_count."""

    def test_increment_read_count(self):
        bookmarks = [make_bookmark(1, read_count=2)]
        updated = core.increment_read_count(bookmarks, 1)
        self.assertEqual(updated[0][6], 3)

    def test_increment_updates_last_read_date_format(self):
        bookmarks = [make_bookmark(1, last_read_date="2020-01-01 00:00:00")]
        updated = core.increment_read_count(bookmarks, 1)
        self.assertRegex(updated[0][5], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_increment_unknown_id_leaves_list_unchanged(self):
        bookmarks = [make_bookmark(1)]
        updated = core.increment_read_count(bookmarks, 99)
        self.assertEqual(updated, bookmarks)


class TestRm(unittest.TestCase):
    """Tests for core.rm."""

    def test_rm_removes_matching_bookmark(self):
        bookmarks = [make_bookmark(1), make_bookmark(2)]
        updated = core.rm(bookmarks, 1)
        self.assertEqual(updated, [make_bookmark(2)])

    def test_rm_unknown_id_leaves_list_unchanged(self):
        bookmarks = [make_bookmark(1)]
        updated = core.rm(bookmarks, 99)
        self.assertEqual(updated, bookmarks)

    def test_rm_clears_dangling_related_ids(self):
        bookmarks = [make_bookmark(1, related_ids=(2,)), make_bookmark(2, related_ids=(1,))]
        updated = core.rm(bookmarks, 1)
        self.assertEqual(updated, [make_bookmark(2, related_ids=())])


class TestLink(unittest.TestCase):
    """Tests for core.link."""

    def test_link_adds_bidirectional_relation(self):
        bookmarks = [make_bookmark(1), make_bookmark(2)]
        updated = core.link(bookmarks, 1, 2)
        self.assertEqual(core.find(updated, 1)[8], (2,))
        self.assertEqual(core.find(updated, 2)[8], (1,))

    def test_link_is_idempotent(self):
        bookmarks = [make_bookmark(1), make_bookmark(2)]
        updated = core.link(core.link(bookmarks, 1, 2), 1, 2)
        self.assertEqual(core.find(updated, 1)[8], (2,))

    def test_link_remove_clears_relation(self):
        bookmarks = [make_bookmark(1, related_ids=(2,)), make_bookmark(2, related_ids=(1,))]
        updated = core.link(bookmarks, 1, 2, remove=True)
        self.assertEqual(core.find(updated, 1)[8], ())
        self.assertEqual(core.find(updated, 2)[8], ())

    def test_link_unknown_id_leaves_list_unchanged(self):
        bookmarks = [make_bookmark(1)]
        updated = core.link(bookmarks, 1, 99)
        self.assertEqual(updated, bookmarks)


class TestShow(unittest.TestCase):
    """Tests for core.show."""

    def test_show_prints_header_and_rows(self):
        bookmarks = [make_bookmark(1, title="Title", labels=("work",))]
        output = io.StringIO()
        with redirect_stdout(output):
            core.show(bookmarks, DEFAULT_CONFIG)
        self.assertIn("Title", output.getvalue())
        self.assertIn("Id", output.getvalue())
        self.assertIn("work", output.getvalue())

    def test_show_sorts_by_id(self):
        bookmarks = [make_bookmark(2, title="Second"), make_bookmark(1, title="First")]
        output = io.StringIO()
        with redirect_stdout(output):
            core.show(bookmarks, DEFAULT_CONFIG)
        text = output.getvalue()
        self.assertLess(text.index("First"), text.index("Second"))

    def test_show_empty_list_prints_header_only(self):
        output = io.StringIO()
        with redirect_stdout(output):
            core.show([], DEFAULT_CONFIG)
        self.assertIn("Id", output.getvalue())


class TestRenderTable(unittest.TestCase):
    """Tests for core.render_table."""

    def test_prints_header_and_row(self):
        output = io.StringIO()
        with redirect_stdout(output):
            core.render_table(("A", "B"), [("1", "2")])
        text = output.getvalue()
        self.assertIn("A", text)
        self.assertIn("1", text)

    def test_columns_are_sized_to_widest_cell(self):
        output = io.StringIO()
        with redirect_stdout(output):
            core.render_table(("A",), [("looooong",)])
        border_line = output.getvalue().splitlines()[0]
        self.assertEqual(len(border_line), len("+----------+"))


class TestBookmarkRow(unittest.TestCase):
    """Tests for core.bookmark_row."""

    def test_joins_labels_and_related_ids(self):
        bookmark = make_bookmark(1, labels=("work", "important"), related_ids=(2, 3))
        row = core.bookmark_row(bookmark, DEFAULT_CONFIG)
        self.assertEqual(row[7], "work,important")
        self.assertEqual(row[8], "2,3")

    def test_marks_stale_bookmark_with_reminder(self):
        bookmark = make_bookmark(1, last_read_date="2000-01-01 00:00:00")
        row = core.bookmark_row(bookmark, DEFAULT_CONFIG)
        self.assertEqual(row[9], "!")

    def test_does_not_mark_recently_read_bookmark(self):
        recent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bookmark = make_bookmark(1, last_read_date=recent)
        row = core.bookmark_row(bookmark, DEFAULT_CONFIG)
        self.assertEqual(row[9], "")


if __name__ == "__main__":
    unittest.main()

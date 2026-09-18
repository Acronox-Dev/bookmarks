'''
Integration tests for the src.commands module, exercising real file I/O.
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import os
import tempfile
import unittest

from src import commands
from src.utils import parse_bookmarks


class BaseCommandsTest(unittest.TestCase):
    """Shared setUp/tearDown creating a temporary bookmarks file."""

    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        os.close(fd)

    def tearDown(self):
        os.remove(self.path)

    def read_bookmarks(self):
        """Read and parse the current content of the temporary bookmarks file."""
        with open(self.path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return parse_bookmarks(lines)


class TestAddCommand(BaseCommandsTest):
    """Tests for commands.add."""

    def test_add_writes_bookmark_to_file(self):
        commands.add(("Title", "https://example.com", "Notes"), self.path, [])
        bookmarks = self.read_bookmarks()
        self.assertEqual(len(bookmarks), 1)
        self.assertEqual(bookmarks[0][1:4], ("Title", "https://example.com", "Notes"))

    def test_add_refuses_duplicate_url(self):
        commands.add(("Title", "https://example.com", "Notes"), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.add(("Other", "https://example.com", "Other notes"), self.path, bookmarks)
        bookmarks_after = self.read_bookmarks()
        self.assertEqual(len(bookmarks_after), 1)


class TestModifyCommand(BaseCommandsTest):
    """Tests for commands.modify."""

    def test_modify_updates_matching_bookmark(self):
        commands.add(("Title", "https://example.com", "Notes"), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.modify(bookmarks[0][0], ("New Title", "https://new.com", "New notes"),
                         self.path, bookmarks)
        updated = self.read_bookmarks()
        self.assertEqual(updated[0][1:4], ("New Title", "https://new.com", "New notes"))

    def test_modify_unknown_id_does_not_change_file(self):
        commands.add(("Title", "https://example.com", "Notes"), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.modify(999, ("New Title", "https://new.com", "New notes"),
                         self.path, bookmarks)
        self.assertEqual(self.read_bookmarks(), bookmarks)


class TestRmCommand(BaseCommandsTest):
    """Tests for commands.rm."""

    def test_rm_removes_matching_bookmark(self):
        commands.add(("Title", "https://example.com", "Notes"), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.rm(bookmarks[0][0], self.path, bookmarks)
        self.assertEqual(self.read_bookmarks(), [])

    def test_rm_unknown_id_does_not_change_file(self):
        commands.add(("Title", "https://example.com", "Notes"), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.rm(999, self.path, bookmarks)
        self.assertEqual(self.read_bookmarks(), bookmarks)


class TestReadCommand(BaseCommandsTest):
    """Tests for commands.read."""

    def test_read_increments_read_count(self):
        commands.add(("Title", "https://example.com", "Notes"), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.read(bookmarks[0][0], self.path, bookmarks)
        updated = self.read_bookmarks()
        self.assertEqual(updated[0][6], 1)

    def test_read_sets_last_read_date_format(self):
        commands.add(("Title", "https://example.com", "Notes"), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.read(bookmarks[0][0], self.path, bookmarks)
        updated = self.read_bookmarks()
        self.assertRegex(updated[0][5], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_read_unknown_id_does_not_change_file(self):
        commands.add(("Title", "https://example.com", "Notes"), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.read(999, self.path, bookmarks)
        self.assertEqual(self.read_bookmarks(), bookmarks)


if __name__ == "__main__":
    unittest.main()

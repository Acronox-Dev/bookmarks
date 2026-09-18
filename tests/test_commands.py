'''
Integration tests for the src.commands module, exercising real file I/O.
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from src import commands
from src.config import DEFAULT_CONFIG
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
        commands.add(("Title", "https://example.com", "Notes", ("work",)), self.path, [])
        bookmarks = self.read_bookmarks()
        self.assertEqual(len(bookmarks), 1)
        self.assertEqual(bookmarks[0][1:4], ("Title", "https://example.com", "Notes"))
        self.assertEqual(bookmarks[0][7], ("work",))

    def test_add_refuses_duplicate_url(self):
        commands.add(("Title", "https://example.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.add(
            ("Other", "https://example.com", "Other notes", ()), self.path, bookmarks
        )
        bookmarks_after = self.read_bookmarks()
        self.assertEqual(len(bookmarks_after), 1)


class TestModifyCommand(BaseCommandsTest):
    """Tests for commands.modify."""

    def test_modify_updates_matching_bookmark(self):
        commands.add(("Title", "https://example.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.modify(
            bookmarks[0][0], ("New Title", "https://new.com", "New notes", ("work",)),
            self.path, bookmarks
        )
        updated = self.read_bookmarks()
        self.assertEqual(updated[0][1:4], ("New Title", "https://new.com", "New notes"))
        self.assertEqual(updated[0][7], ("work",))

    def test_modify_unknown_id_does_not_change_file(self):
        commands.add(("Title", "https://example.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.modify(
            999, ("New Title", "https://new.com", "New notes", ()), self.path, bookmarks
        )
        self.assertEqual(self.read_bookmarks(), bookmarks)


class TestRmCommand(BaseCommandsTest):
    """Tests for commands.rm."""

    def test_rm_removes_matching_bookmark(self):
        commands.add(("Title", "https://example.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.rm(bookmarks[0][0], self.path, bookmarks)
        self.assertEqual(self.read_bookmarks(), [])

    def test_rm_unknown_id_does_not_change_file(self):
        commands.add(("Title", "https://example.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.rm(999, self.path, bookmarks)
        self.assertEqual(self.read_bookmarks(), bookmarks)


class TestReadCommand(BaseCommandsTest):
    """Tests for commands.read."""

    def test_read_increments_read_count(self):
        commands.add(("Title", "https://example.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.read(bookmarks[0][0], self.path, bookmarks, DEFAULT_CONFIG)
        updated = self.read_bookmarks()
        self.assertEqual(updated[0][6], 1)

    def test_read_sets_last_read_date_format(self):
        commands.add(("Title", "https://example.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.read(bookmarks[0][0], self.path, bookmarks, DEFAULT_CONFIG)
        updated = self.read_bookmarks()
        self.assertRegex(updated[0][5], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_read_unknown_id_does_not_change_file(self):
        commands.add(("Title", "https://example.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.read(999, self.path, bookmarks, DEFAULT_CONFIG)
        self.assertEqual(self.read_bookmarks(), bookmarks)


class TestRelatedCommand(BaseCommandsTest):
    """Tests for commands.related."""

    def test_related_links_two_bookmarks(self):
        commands.add(("A", "https://a.com", "Notes", ()), self.path, [])
        commands.add(("B", "https://b.com", "Notes", ()), self.path, self.read_bookmarks())
        bookmarks = self.read_bookmarks()
        commands.related(bookmarks[0][0], bookmarks[1][0], self.path, bookmarks, False)
        updated = self.read_bookmarks()
        self.assertEqual(updated[0][8], (updated[1][0],))
        self.assertEqual(updated[1][8], (updated[0][0],))

    def test_related_remove_unlinks_two_bookmarks(self):
        commands.add(("A", "https://a.com", "Notes", ()), self.path, [])
        commands.add(("B", "https://b.com", "Notes", ()), self.path, self.read_bookmarks())
        bookmarks = self.read_bookmarks()
        commands.related(bookmarks[0][0], bookmarks[1][0], self.path, bookmarks, False)
        linked = self.read_bookmarks()
        commands.related(linked[0][0], linked[1][0], self.path, linked, True)
        updated = self.read_bookmarks()
        self.assertEqual(updated[0][8], ())
        self.assertEqual(updated[1][8], ())

    def test_related_unknown_id_does_not_change_file(self):
        commands.add(("A", "https://a.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.related(bookmarks[0][0], 999, self.path, bookmarks, False)
        self.assertEqual(self.read_bookmarks(), bookmarks)


class TestSequenceCommand(BaseCommandsTest):
    """Tests for commands.sequence."""

    def test_sequence_prints_recommended_order(self):
        commands.add(("A", "https://a.com", "Notes", ()), self.path, [])
        commands.add(("B", "https://b.com", "Notes", ()), self.path, self.read_bookmarks())
        bookmarks = self.read_bookmarks()
        commands.related(bookmarks[0][0], bookmarks[1][0], self.path, bookmarks, False)
        linked = self.read_bookmarks()

        output = io.StringIO()
        with redirect_stdout(output):
            commands.sequence(linked, linked[0][0])
        text = output.getvalue()
        self.assertIn("A", text)
        self.assertIn("B", text)

    def test_sequence_unknown_id_prints_empty_line(self):
        output = io.StringIO()
        with redirect_stdout(output):
            commands.sequence([], 999)
        self.assertEqual(output.getvalue(), "\n")


class TestExportImportCommands(BaseCommandsTest):
    """Tests for commands.export and commands.import_bookmarks."""

    def setUp(self):
        super().setUp()
        fd, self.export_path = tempfile.mkstemp()
        os.close(fd)

    def tearDown(self):
        os.remove(self.export_path)
        super().tearDown()

    def test_export_then_import_round_trips_into_a_fresh_file(self):
        commands.add(("Title", "https://example.com", "Notes", ("work",)), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.export(bookmarks, "json", self.export_path)

        fd, other_path = tempfile.mkstemp()
        os.close(fd)
        try:
            commands.import_bookmarks([], "json", self.export_path, other_path)
            with open(other_path, 'r', encoding='utf-8') as f:
                imported = parse_bookmarks(f.readlines())
            self.assertEqual(imported[0][1:4], ("Title", "https://example.com", "Notes"))
            self.assertEqual(imported[0][7], ("work",))
        finally:
            os.remove(other_path)

    def test_import_merges_with_existing_bookmarks(self):
        commands.add(("A", "https://a.com", "Notes", ()), self.path, [])
        bookmarks = self.read_bookmarks()
        commands.export(bookmarks, "csv", self.export_path)

        commands.add(("B", "https://b.com", "Notes", ()), self.path, bookmarks)
        bookmarks = self.read_bookmarks()
        commands.import_bookmarks(bookmarks, "csv", self.export_path, self.path)

        merged = self.read_bookmarks()
        self.assertEqual({b[2] for b in merged}, {"https://a.com", "https://b.com"})


class TestMergeCommand(unittest.TestCase):
    """Tests for commands.merge."""

    def setUp(self):
        fd, self.path_a = tempfile.mkstemp()
        os.close(fd)
        fd, self.path_b = tempfile.mkstemp()
        os.close(fd)
        fd, self.output_path = tempfile.mkstemp()
        os.close(fd)

    def tearDown(self):
        for path in (self.path_a, self.path_b, self.output_path):
            os.remove(path)

    def test_merge_combines_two_files(self):
        commands.add(("A", "https://a.com", "Notes", ()), self.path_a, [])
        commands.add(("B", "https://b.com", "Notes", ()), self.path_b, [])
        commands.merge([self.path_a, self.path_b], self.output_path)
        with open(self.output_path, 'r', encoding='utf-8') as f:
            merged = parse_bookmarks(f.readlines())
        self.assertEqual({b[2] for b in merged}, {"https://a.com", "https://b.com"})
        self.assertEqual([b[0] for b in merged], [1, 2])


if __name__ == "__main__":
    unittest.main()

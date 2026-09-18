'''
Unit tests for the src.io_formats module (export/import JSON and CSV).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import os
import tempfile
import unittest

from src import io_formats

BOOKMARK = (
    1, "Title", "https://example.com", "Notes", "2026-01-01 00:00:00",
    "2026-01-01 00:00:00", 3, ("work", "urgent"), (2, 3)
)


class BaseIOFormatsTest(unittest.TestCase):
    """Shared setUp/tearDown creating a temporary export/import file."""

    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        os.close(fd)

    def tearDown(self):
        os.remove(self.path)


class TestJson(BaseIOFormatsTest):
    """Tests for export_json/import_json."""

    def test_round_trip_preserves_the_bookmark(self):
        io_formats.export_json([BOOKMARK], self.path)
        result = io_formats.import_json(self.path)
        self.assertEqual(result, [BOOKMARK])

    def test_export_writes_valid_json(self):
        io_formats.export_json([BOOKMARK], self.path)
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("\"title\": \"Title\"", content)


class TestCsv(BaseIOFormatsTest):
    """Tests for export_csv/import_csv."""

    def test_round_trip_preserves_the_bookmark(self):
        io_formats.export_csv([BOOKMARK], self.path)
        result = io_formats.import_csv(self.path)
        self.assertEqual(result, [BOOKMARK])

    def test_export_writes_a_header_row(self):
        io_formats.export_csv([BOOKMARK], self.path)
        with open(self.path, 'r', encoding='utf-8') as f:
            header = f.readline()
        self.assertIn("title", header)

    def test_round_trip_handles_empty_labels_and_related_ids(self):
        bookmark = BOOKMARK[:7] + ((), ())
        io_formats.export_csv([bookmark], self.path)
        result = io_formats.import_csv(self.path)
        self.assertEqual(result, [bookmark])


class TestExportImportBookmarks(BaseIOFormatsTest):
    """Tests for export_bookmarks/import_bookmarks dispatch."""

    def test_export_bookmarks_dispatches_to_json(self):
        io_formats.export_bookmarks([BOOKMARK], "json", self.path)
        self.assertEqual(io_formats.import_bookmarks("json", self.path), [BOOKMARK])

    def test_export_bookmarks_dispatches_to_csv(self):
        io_formats.export_bookmarks([BOOKMARK], "csv", self.path)
        self.assertEqual(io_formats.import_bookmarks("csv", self.path), [BOOKMARK])


if __name__ == "__main__":
    unittest.main()

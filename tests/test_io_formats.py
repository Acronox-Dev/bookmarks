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


class TestHtml(BaseIOFormatsTest):
    """Tests for export_html/import_html (Firefox/Chrome bookmarks)."""

    def test_export_writes_a_netscape_header(self):
        io_formats.export_html([BOOKMARK], self.path)
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("NETSCAPE-Bookmark-file-1", content)
        self.assertIn('HREF="https://example.com"', content)
        self.assertIn('TAGS="work,urgent"', content)

    def test_round_trip_preserves_url_title_notes_and_labels(self):
        io_formats.export_html([BOOKMARK], self.path)
        result = io_formats.import_html(self.path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1:4], ("Title", "https://example.com", "Notes"))
        self.assertEqual(set(result[0][7]), {"work", "urgent"})

    def test_round_trip_preserves_dates(self):
        io_formats.export_html([BOOKMARK], self.path)
        result = io_formats.import_html(self.path)
        self.assertEqual(result[0][4], "2026-01-01 00:00:00")
        self.assertEqual(result[0][5], "2026-01-01 00:00:00")

    def test_import_assigns_sequential_ids(self):
        second = BOOKMARK[:2] + ("https://other.com",) + BOOKMARK[3:]
        io_formats.export_html([BOOKMARK, second], self.path)
        result = io_formats.import_html(self.path)
        self.assertEqual([b[0] for b in result], [1, 2])

    def test_imports_a_real_firefox_style_export(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(
                '<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
                '<DL><p>\n'
                '    <DT><A HREF="https://example.com" ADD_DATE="1700000000" '
                'LAST_MODIFIED="1700000100">Example</A>\n'
                '    <DD>A short description\n'
                '</DL><p>\n'
            )
        result = io_formats.import_html(self.path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Example")
        self.assertEqual(result[0][3], "A short description")


class TestMarkdown(BaseIOFormatsTest):
    """Tests for export_markdown (export-only)."""

    def test_export_writes_a_markdown_list_item(self):
        io_formats.export_markdown([BOOKMARK], self.path)
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("[Title](https://example.com)", content)
        self.assertIn("work, urgent", content)
        self.assertIn("Notes", content)

    def test_markdown_has_no_importer(self):
        self.assertNotIn("markdown", io_formats.IMPORTERS)


class TestExportImportBookmarks(BaseIOFormatsTest):
    """Tests for export_bookmarks/import_bookmarks dispatch."""

    def test_export_bookmarks_dispatches_to_json(self):
        io_formats.export_bookmarks([BOOKMARK], "json", self.path)
        self.assertEqual(io_formats.import_bookmarks("json", self.path), [BOOKMARK])

    def test_export_bookmarks_dispatches_to_csv(self):
        io_formats.export_bookmarks([BOOKMARK], "csv", self.path)
        self.assertEqual(io_formats.import_bookmarks("csv", self.path), [BOOKMARK])

    def test_export_bookmarks_dispatches_to_html(self):
        io_formats.export_bookmarks([BOOKMARK], "html", self.path)
        result = io_formats.import_bookmarks("html", self.path)
        self.assertEqual(result[0][1:4], ("Title", "https://example.com", "Notes"))

    def test_export_bookmarks_dispatches_to_markdown(self):
        io_formats.export_bookmarks([BOOKMARK], "markdown", self.path)
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("# Bookmarks", content)


if __name__ == "__main__":
    unittest.main()

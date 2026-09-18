'''
Unit tests for the src.utils module (validation, formatting, file I/O helpers).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import os
import tempfile
import unittest
from types import SimpleNamespace

from src import utils


class TestIsUrlValid(unittest.TestCase):
    """Tests for utils.is_url_valid."""

    def test_valid_http_url(self):
        self.assertTrue(utils.is_url_valid("http://example.com"))

    def test_valid_https_url(self):
        self.assertTrue(utils.is_url_valid("https://example.com"))

    def test_missing_scheme_is_invalid(self):
        self.assertFalse(utils.is_url_valid("example.com"))

    def test_unsupported_scheme_is_invalid(self):
        self.assertFalse(utils.is_url_valid("ftp://example.com"))

    def test_empty_string_is_invalid(self):
        self.assertFalse(utils.is_url_valid(""))


class TestValidateOptionTypes(unittest.TestCase):
    """Tests for utils.validate_option_types."""

    def test_valid_options_return_true(self):
        options = SimpleNamespace(t="Title", u="https://example.com", n="Notes", id="3")
        self.assertTrue(utils.validate_option_types(options))

    def test_valid_id_is_cast_to_int(self):
        options = SimpleNamespace(id="3")
        utils.validate_option_types(options)
        self.assertEqual(options.id, 3)

    def test_non_numeric_id_returns_false(self):
        options = SimpleNamespace(id="abc")
        self.assertFalse(utils.validate_option_types(options))

    def test_non_string_title_returns_false(self):
        options = SimpleNamespace(t=42)
        self.assertFalse(utils.validate_option_types(options))

    def test_missing_attributes_are_ignored(self):
        options = SimpleNamespace(command="show")
        self.assertTrue(utils.validate_option_types(options))

    def test_non_string_labels_returns_false(self):
        options = SimpleNamespace(l=42)
        self.assertFalse(utils.validate_option_types(options))

    def test_id1_and_id2_are_cast_to_int(self):
        options = SimpleNamespace(id1="1", id2="2")
        utils.validate_option_types(options)
        self.assertEqual((options.id1, options.id2), (1, 2))


class TestFormatTitle(unittest.TestCase):
    """Tests for utils.format_title."""

    def test_strips_whitespace(self):
        self.assertEqual(utils.format_title("  Title  "), "Title")

    def test_truncates_to_64_chars(self):
        self.assertEqual(len(utils.format_title("a" * 100)), 64)

    def test_removes_semicolons(self):
        self.assertEqual(utils.format_title("Ti;tle"), "Title")


class TestFormatUrl(unittest.TestCase):
    """Tests for utils.format_url."""

    def test_adds_http_scheme_when_missing(self):
        self.assertEqual(utils.format_url("example.com"), "http://example.com")

    def test_keeps_https_scheme(self):
        self.assertEqual(utils.format_url("https://example.com"), "https://example.com")

    def test_invalid_url_returns_none(self):
        self.assertIsNone(utils.format_url(""))


class TestFormatNotes(unittest.TestCase):
    """Tests for utils.format_notes."""

    def test_strips_whitespace(self):
        self.assertEqual(utils.format_notes("  Notes  "), "Notes")

    def test_removes_semicolons_and_newlines(self):
        self.assertEqual(utils.format_notes("No;tes\n"), "Notes")


class TestFormatLabels(unittest.TestCase):
    """Tests for utils.format_labels."""

    def test_splits_on_comma_and_strips(self):
        self.assertEqual(utils.format_labels(" work , important "), ("work", "important"))

    def test_drops_empty_labels(self):
        self.assertEqual(utils.format_labels("work,,important,"), ("work", "important"))

    def test_deduplicates_keeping_first_occurrence(self):
        self.assertEqual(utils.format_labels("work,work,important"), ("work", "important"))

    def test_empty_string_returns_empty_tuple(self):
        self.assertEqual(utils.format_labels(""), ())


class TestWriteBookmarks(unittest.TestCase):
    """Tests for utils.write_bookmarks."""

    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        os.close(fd)

    def tearDown(self):
        os.remove(self.path)

    def test_write_overwrites_file_content(self):
        bookmark = (1, "Title", "https://example.com", "Notes",
                    "2026-01-01 00:00:00", "2026-01-01 00:00:00", 0,
                    ("work", "important"), (2, 3))
        utils.write_bookmarks(self.path, 'w', [bookmark])
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(
            content,
            "1; Title; https://example.com; Notes; 2026-01-01 00:00:00; "
            "2026-01-01 00:00:00; 0; work,important; 2,3\n"
        )

    def test_write_serializes_empty_labels_and_related_ids(self):
        bookmark = (1, "Title", "https://example.com", "Notes",
                    "2026-01-01 00:00:00", "2026-01-01 00:00:00", 0, (), ())
        utils.write_bookmarks(self.path, 'w', [bookmark])
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(
            content,
            "1; Title; https://example.com; Notes; 2026-01-01 00:00:00; "
            "2026-01-01 00:00:00; 0; ; \n"
        )

    def test_write_appends_to_existing_content(self):
        bookmark = (1, "Title", "https://example.com", "Notes",
                    "2026-01-01 00:00:00", "2026-01-01 00:00:00", 0, (), ())
        utils.write_bookmarks(self.path, 'w', [bookmark])
        utils.write_bookmarks(self.path, 'a', [bookmark])
        with open(self.path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)


class TestParseBookmarks(unittest.TestCase):
    """Tests for utils.parse_bookmarks."""

    def test_parses_a_single_line(self):
        lines = ["1; Title; https://example.com; Notes; 2026-01-01 00:00:00; "
                  "2026-01-01 00:00:00; 0; work,important; 2,3\n"]
        bookmarks = utils.parse_bookmarks(lines)
        self.assertEqual(
            bookmarks,
            [(1, "Title", "https://example.com", "Notes",
              "2026-01-01 00:00:00", "2026-01-01 00:00:00", 0,
              ("work", "important"), (2, 3))]
        )

    def test_parses_empty_labels_and_related_ids(self):
        lines = ["1; Title; https://example.com; Notes; 2026-01-01 00:00:00; "
                  "2026-01-01 00:00:00; 0; ; \n"]
        bookmarks = utils.parse_bookmarks(lines)
        self.assertEqual(bookmarks[0][7], ())
        self.assertEqual(bookmarks[0][8], ())

    def test_ignores_blank_lines(self):
        lines = ["1; Title; https://example.com; Notes; 2026-01-01 00:00:00; "
                  "2026-01-01 00:00:00; 0; ; \n", "\n", "   \n"]
        bookmarks = utils.parse_bookmarks(lines)
        self.assertEqual(len(bookmarks), 1)

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(utils.parse_bookmarks([]), [])


class TestUrlDuplicateDetection(unittest.TestCase):
    """Tests for utils.url_duplicate_detection."""

    def test_detects_existing_url(self):
        bookmarks = [(1, "Title", "https://example.com", "Notes",
                       "2026-01-01 00:00:00", "2026-01-01 00:00:00", 0, (), ())]
        details = ("New", "https://example.com", "new", ())
        self.assertTrue(utils.url_duplicate_detection(details, bookmarks))

    def test_new_url_is_not_a_duplicate(self):
        bookmarks = [(1, "Title", "https://example.com", "Notes",
                       "2026-01-01 00:00:00", "2026-01-01 00:00:00", 0, (), ())]
        details = ("New", "https://other.com", "new", ())
        self.assertFalse(utils.url_duplicate_detection(details, bookmarks))

    def test_empty_bookmarks_is_never_a_duplicate(self):
        details = ("New", "https://example.com", "new", ())
        self.assertFalse(utils.url_duplicate_detection(details, []))


if __name__ == "__main__":
    unittest.main()

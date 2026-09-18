'''
Unit tests for the src.compliance module (file compliance checks).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import io
import unittest
from contextlib import redirect_stdout

from src import compliance

VALID_LINE = (
    "1; Title; https://example.com; Notes; 2026-01-01 00:00:00; "
    "2026-01-01 00:00:00; 0; ; \n"
)


class TestCheckLines(unittest.TestCase):
    """Tests for compliance.check_lines."""

    def test_valid_line_has_no_issues(self):
        self.assertEqual(compliance.check_lines([VALID_LINE]), [])

    def test_blank_lines_are_ignored(self):
        self.assertEqual(compliance.check_lines([VALID_LINE, "\n", "   \n"]), [])

    def test_wrong_field_count_is_reported(self):
        issues = compliance.check_lines(["1; Title; https://example.com\n"])
        self.assertEqual(len(issues), 1)
        self.assertIn("expected 9 fields", issues[0])

    def test_non_numeric_id_is_reported(self):
        line = VALID_LINE.replace("1;", "abc;", 1)
        issues = compliance.check_lines([line])
        self.assertTrue(any("not a positive integer" in issue for issue in issues))

    def test_duplicate_id_is_reported(self):
        issues = compliance.check_lines([VALID_LINE, VALID_LINE])
        self.assertTrue(any("duplicate id" in issue for issue in issues))

    def test_invalid_url_is_reported(self):
        line = VALID_LINE.replace("https://example.com", "not a url")
        issues = compliance.check_lines([line])
        self.assertTrue(any("is not valid" in issue for issue in issues))

    def test_invalid_date_is_reported(self):
        line = VALID_LINE.replace("2026-01-01 00:00:00; 2026-01-01 00:00:00",
                                   "not-a-date; 2026-01-01 00:00:00")
        issues = compliance.check_lines([line])
        self.assertTrue(any("does not match" in issue for issue in issues))

    def test_non_numeric_read_count_is_reported(self):
        line = VALID_LINE.replace("; 0; ", "; many; ")
        issues = compliance.check_lines([line])
        self.assertTrue(any("read_count" in issue for issue in issues))

    def test_title_over_64_chars_is_reported(self):
        line = VALID_LINE.replace("Title", "T" * 65)
        issues = compliance.check_lines([line])
        self.assertTrue(any("exceeds 64 characters" in issue for issue in issues))


class TestPrintCheck(unittest.TestCase):
    """Tests for compliance.print_check."""

    def test_prints_confirmation_when_no_issues(self):
        output = io.StringIO()
        with redirect_stdout(output):
            compliance.print_check([VALID_LINE])
        self.assertIn("No compliance issues", output.getvalue())

    def test_prints_each_issue(self):
        output = io.StringIO()
        with redirect_stdout(output):
            compliance.print_check(["1; Title; https://example.com\n"])
        self.assertIn("expected 9 fields", output.getvalue())


if __name__ == "__main__":
    unittest.main()

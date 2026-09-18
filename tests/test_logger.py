'''
Unit tests for the src.logger module (log management).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import os
import tempfile
import unittest

from src import logger


class TestLogAction(unittest.TestCase):
    """Tests for logger.log_action."""

    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        os.close(fd)
        self.config = {"log_file": self.path}

    def tearDown(self):
        os.remove(self.path)

    def test_appends_a_line_with_command_and_detail(self):
        logger.log_action(self.config, "add", "t=Title")
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("add", content)
        self.assertIn("t=Title", content)

    def test_appends_a_timestamp(self):
        logger.log_action(self.config, "add", "t=Title")
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertRegex(content, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2};")

    def test_multiple_actions_append_multiple_lines(self):
        logger.log_action(self.config, "add", "t=Title")
        logger.log_action(self.config, "rm", "id=1")
        with open(self.path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)


if __name__ == "__main__":
    unittest.main()

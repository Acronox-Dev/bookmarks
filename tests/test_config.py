'''
Unit tests for the src.config module (configuration management).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import json
import os
import tempfile
import unittest

from src import config


class TestLoadConfig(unittest.TestCase):
    """Tests for config.load_config."""

    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        os.close(fd)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_missing_file_returns_defaults(self):
        os.remove(self.path)
        self.assertEqual(config.load_config(self.path), config.DEFAULT_CONFIG)

    def test_invalid_json_returns_defaults(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write("not json")
        self.assertEqual(config.load_config(self.path), config.DEFAULT_CONFIG)

    def test_file_overrides_defaults(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump({"reading_reminder_days": 7}, f)
        loaded = config.load_config(self.path)
        self.assertEqual(loaded["reading_reminder_days"], 7)

    def test_file_keeps_unspecified_defaults(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump({"reading_reminder_days": 7}, f)
        loaded = config.load_config(self.path)
        self.assertEqual(loaded["log_file"], config.DEFAULT_CONFIG["log_file"])


if __name__ == "__main__":
    unittest.main()

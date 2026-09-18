'''
Unit tests for the src.labels module (URL classification + categories).
'''

# pylint: disable=missing-function-docstring
# Test method names are descriptive enough to document their own intent.

import unittest

from src import labels
from src.config import DEFAULT_CONFIG


class TestClassify(unittest.TestCase):
    """Tests for labels.classify."""

    def test_adds_label_matching_url_rule(self):
        config = {**DEFAULT_CONFIG, "url_label_rules": {"github.com": "dev"}}
        result = labels.classify("https://github.com/x", (), config)
        self.assertEqual(result, ("dev",))

    def test_keeps_existing_labels(self):
        config = {**DEFAULT_CONFIG, "url_label_rules": {"github.com": "dev"}}
        result = labels.classify("https://github.com/x", ("work",), config)
        self.assertEqual(result, ("work", "dev"))

    def test_does_not_duplicate_an_already_present_label(self):
        config = {**DEFAULT_CONFIG, "url_label_rules": {"github.com": "dev"}}
        result = labels.classify("https://github.com/x", ("dev",), config)
        self.assertEqual(result, ("dev",))

    def test_no_matching_rule_leaves_labels_unchanged(self):
        config = {**DEFAULT_CONFIG, "url_label_rules": {"github.com": "dev"}}
        result = labels.classify("https://example.com", ("work",), config)
        self.assertEqual(result, ("work",))

    def test_empty_rules_leave_labels_unchanged(self):
        result = labels.classify("https://example.com", ("work",), DEFAULT_CONFIG)
        self.assertEqual(result, ("work",))


class TestCategoryOf(unittest.TestCase):
    """Tests for labels.category_of."""

    def test_returns_configured_category(self):
        config = {**DEFAULT_CONFIG, "label_categories": {"work": "professional"}}
        self.assertEqual(labels.category_of("work", config), "professional")

    def test_returns_none_for_uncategorized_label(self):
        self.assertIsNone(labels.category_of("work", DEFAULT_CONFIG))


class TestRootCategoryOf(unittest.TestCase):
    """Tests for labels.root_category_of."""

    def test_category_without_parent_is_its_own_root(self):
        self.assertEqual(labels.root_category_of("professional", DEFAULT_CONFIG), "professional")

    def test_walks_up_to_the_top_level_ancestor(self):
        config = {
            **DEFAULT_CONFIG,
            "category_parents": {"urgent": "professional", "professional": "life"}
        }
        self.assertEqual(labels.root_category_of("urgent", config), "life")


if __name__ == "__main__":
    unittest.main()

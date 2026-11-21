"""
test_taxonomy.py - Unit Tests for Space Debris Taxonomy and Class Mappings
"""

import unittest
from src.config import CLASS_NAMES, OPERATIONAL_STATES, STATE_HAZARDOUS, STATE_ACTIVE
from src.taxonomy import get_category_for_class, get_display_name, OPERATIONAL_CATEGORIES


class TestTaxonomy(unittest.TestCase):

    def test_class_names_count(self):
        self.assertEqual(len(CLASS_NAMES), 11)

    def test_operational_states(self):
        self.assertEqual(len(OPERATIONAL_STATES), 4)

    def test_get_category_debris(self):
        cat = get_category_for_class("debris")
        self.assertEqual(cat.category_id, "TRACKABLE_DEBRIS")
        self.assertFalse(cat.is_serviceable)

    def test_get_category_cheops(self):
        cat = get_category_for_class("cheops")
        self.assertEqual(cat.category_id, "SCIENTIFIC_PAYLOAD")
        self.assertTrue(cat.is_serviceable)

    def test_display_name(self):
        name = get_display_name("cheops")
        self.assertIn("CHEOPS", name)


if __name__ == "__main__":
    unittest.main()

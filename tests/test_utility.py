"""Test the utility module"""
import unittest
import xmlrunner
from custom_components.purei9 import utility

class TestUtility(unittest.TestCase):
    """Tests for the utility module"""
    data_first_or_default = [
        ([1, 2, 3], lambda x: x == 2, None, 2),
        ([1, 2, 3], lambda x: x == 4, "x", "x"),
    ]

    def test_first_or_default(self):
        """Test the first_or_default function"""
        for collection, predicate, default, expected in self.data_first_or_default:
            with self.subTest():
                self.assertEqual(expected,
                    utility.first_or_default(collection, predicate, default))

    data_array_join = [
        ([1, 2, 3], "-", "1-2-3"),
        (["a", None, "b", 4], "_", "a_b_4"),
        (["x", "", "y", "", "", "z"], "--", "x--y--z"),
        [[], ".", ""]
    ]

    def test_array_join(self):
        """Test the array_join function"""
        for array, separator, expected in self.data_array_join:
            with self.subTest():
                self.assertEqual(expected,
                    utility.array_join(array, separator))

if __name__ == '__main__':
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output="results")
    )

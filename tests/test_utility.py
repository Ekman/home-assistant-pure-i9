"""Test the utility module"""
import unittest
from custom_components.purei9 import utility

class TestPureI9(unittest.TestCase):
    """Tests for the utility module"""
    data_array_join = [
        ([1, 2, 3], "-", "1-2-3"),
        (["a", None, "b", 4], "_", "a_b_4"),
    ]

    def test_array_join(self):
        """Test the array_join function"""
        for array, separator, expected in self.data_array_join:
            with self.subTest():
                self.assertEqual(expected,
                    utility.array_join(array_separator))

if __name__ == '__main__':
    unittest.main()

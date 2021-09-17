import math

from intervalg import Interval as In

import unittest


class TestInterval(unittest.TestCase):
    def test_constructor_default(self):
        x = In()
        self.assertTrue(math.isinf(x.lower))
        self.assertTrue(x.lower < 0)
        self.assertTrue(math.isinf(x.upper))
        self.assertTrue(x.upper > 0)
        self.assertEqual((-math.inf, math.inf), x)

    def test_constructor_single_number(self):
        self.assertEqual((3, 3), In(3))
        self.assertEqual((0, 0), In(0))
        self.assertEqual((-10, -10), In(-10))
        self.assertEqual((3.0, 3.0), In(3.0))
        self.assertEqual((0.0, 0.0), In(0.0))
        self.assertEqual((-10.2, -10.2), In(-10.2))
        for val in range(-20, 20):
            x = In(val)
            self.assertIsInstance(x, In)
            self.assertEqual(val, x.lower)
            self.assertEqual(val, x.upper)
            self.assertTrue(x.is_single_number)
            self.assertEqual(val, x)
        for val in range(-20, 20):
            val += 0.1  # To make it float
            x = In(val)
            self.assertIsInstance(x, In)
            self.assertEqual(val, x.lower)
            self.assertEqual(val, x.upper)
            self.assertTrue(x.is_single_number)
            self.assertEqual(val, x)

    def test_constructor_single_number_undefined(self):
        self.assertEqual((-math.inf, math.inf), In(None))
        self.assertEqual((-math.inf, math.inf), In(math.nan))
        self.assertEqual((-math.inf, math.inf), In(math.inf))
        self.assertEqual((-math.inf, math.inf), In(-math.inf))

    def test_constructor_two_values_equal(self):
        self.assertEqual((3, 3), In(3, 3))
        self.assertEqual((0, 0), In(0, 0))
        self.assertEqual((-10, -10), In(-10, -10))
        self.assertEqual((3.0, 3.0), In(3.0, 3.0))
        self.assertEqual((0.0, 0.0), In(0.0, 0.0))
        self.assertEqual((-10.2, -10.2), In(-10.2, -10.2))

    def test_constructor_two_values_rising(self):
        # Integers
        self.assertEqual((3, 4), In(3, 4))
        self.assertEqual((0, 5), In(0, 5))
        self.assertEqual((-10, -2), In(-10, -2))
        self.assertEqual((-10, 0), In(-10, 0))
        self.assertEqual((-10, 3), In(-10, 3))
        # Floats
        self.assertEqual((3, 4.6), In(3, 4.6))
        self.assertEqual((0.6, 5), In(0.6, 5))
        self.assertEqual((-10.6, -2.6), In(-10.6, -2.6))
        self.assertEqual((-10, 0.6), In(-10, 0.6))
        self.assertEqual((-10.6, 3), In(-10.6, 3))

    def test_constructor_two_values_falling(self):
        # Integers
        self.assertEqual((3, 4), In(4, 3))
        self.assertEqual((0, 5), In(5, 0))
        self.assertEqual((-10, -2), In(-2, -10))
        self.assertEqual((-10, 0), In(0, -10))
        self.assertEqual((-10, 3), In(3, -10))
        # Floats
        self.assertEqual((3, 4.6), In(4.6, 3))
        self.assertEqual((0.6, 5), In(5, 0.6))
        self.assertEqual((-10.6, -2.6), In(-2.6, -10.6))
        self.assertEqual((-10, 0.6), In(0.6, -10))
        self.assertEqual((-10.6, 3), In(3, -10.6))

    def test_constructor_string_infinite_interval(self):
        left_brackets = '([]'
        right_brackets = ')]['
        separators = ',:;|'
        undefined = ('', 'None', 'null', 'nan',
                     'inf', '-inf', 'Infinity', '-Infinity')
        for l in left_brackets:
            for lo in undefined:
                for s in separators:
                    for up in undefined:
                        for r in right_brackets:
                            combo = l + lo + s + up + r
                            # Not using self.subTest() for a ~100x speedup
                            self.assertEqual((None, None), In(combo))

    def test_add(self):
        self.assertEqual((4, 6), (1, 2) + In(3, 4))
        self.assertEqual((4, 6), In(1, 2) + (3, 4))
        self.assertEqual((4, 6), In(1, 2) + In(3, 4))
        self.assertEqual((4, 6), (3, 4) + In(1, 2))
        self.assertEqual((4, 6), In(3, 4) + (1, 2))
        self.assertEqual((4, 6), In(3, 4) + In(1, 2))


if __name__ == '__main__':
    unittest.main()

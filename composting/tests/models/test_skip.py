import unittest

from composting.models import Skip


class TestSkip(unittest.TestCase):
    def test_cross_sectional_area(self):
        skip = Skip(small_length=20.0, large_length=30.0, small_breadth=10.0,
                    large_breadth=16.0)
        # (sl + ll) * (sb + lb) /4
        self.assertEqual(skip.cross_sectional_area, 325.0)
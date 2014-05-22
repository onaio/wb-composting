import unittest
import datetime

from composting.libs import utils


class TestUtils(unittest.TestCase):
    def test_get_month_start_end_if_end_month(self):
        date = datetime.date(2014, 2, 28)
        start, end = utils.get_month_start_end(date)
        self.assertEqual(start, datetime.date(2014, 2, 1))
        self.assertEqual(end, datetime.date(2014, 2, 28))

    def test_get_month_start_end_if_end_year(self):
        date = datetime.date(2013, 12, 25)
        start, end = utils.get_month_start_end(date)
        self.assertEqual(start, datetime.date(2013, 12, 1))
        self.assertEqual(end, datetime.date(2013, 12, 31))
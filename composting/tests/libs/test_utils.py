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

    def test_get_previous_month_year(self):
        date = datetime.date(2014, 2, 28)
        previous_month_year = utils.get_previous_month_year(date)
        self.assertEqual(previous_month_year, datetime.date(2014, 1, 1))

    def test_get_previous_month_year_if_new_year(self):
        date = datetime.date(2014, 1, 25)
        previous_month_year = utils.get_previous_month_year(date)
        self.assertEqual(previous_month_year, datetime.date(2013, 12, 1))
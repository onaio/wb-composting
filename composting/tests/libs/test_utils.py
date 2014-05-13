import unittest
import datetime

from composting.libs import utils


class TestUtils(unittest.TestCase):
    def test_remove_time_zone_if_exists(self):
        result = utils.remove_time_zone('2014-04-29T10:35:00.000+03')
        self.assertEqual(result, '2014-04-29T10:35:00.000')

    def test_remove_time_zone_if_not_exists(self):
        result = utils.remove_time_zone('2014-04-29T10:35:00.000')
        self.assertEqual(result, '2014-04-29T10:35:00.000')

    def test_date_string_to_date(self):
        date_string = '2014-04-29T10:35:00.000+03'
        result = utils.date_string_to_date(date_string)
        self.assertEqual(datetime.date(2014, 04, 29), result)

    def test_date_string_to_time(self):
        date_string = '2014-04-29T10:35:00.000+03'
        result = utils.date_string_to_time(date_string)
        self.assertEqual(datetime.time(10, 35, 00), result)
import datetime

from composting.models.base import DBSession
from composting.models.municipality import Municipality
from composting.models.electricity_register import ElectricityRegister
from composting.tests.test_base import TestBase


class TestElectricityRegister(TestBase):
    def setUp(self):
        super(TestElectricityRegister, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_get_last_meter_reading(self):
        current_month_year = datetime.date(2014, 05, 12)
        last_meter_reading = ElectricityRegister.get_last_meter_reading(
            self.municipality, current_month_year)
        self.assertEqual(last_meter_reading, '857.0')

    def test_get_last_meter_reading_returns_none_if_no_result(self):
        current_month_year = datetime.date(2014, 01, 12)
        last_meter_reading = ElectricityRegister.get_last_meter_reading(
            self.municipality, current_month_year)
        self.assertIsNone(last_meter_reading)

    def test_consumption_since_last_reading(self):
        electricity_register = ElectricityRegister.newest()
        consumption = electricity_register.consumption_since_last_reading(
            self.municipality)
        self.assertEqual(consumption, 1208.0 - 857.0)

    def test_consumption_since_last_reading_returns_none_if_none(self):
        electricity_register = DBSession\
            .query(ElectricityRegister)\
            .filter(ElectricityRegister.date == '2014-04-01')\
            .one()
        consumption = electricity_register.consumption_since_last_reading(
            self.municipality)
        self.assertIsNone(consumption)
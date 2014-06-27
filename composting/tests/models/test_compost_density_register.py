from datetime import date

from composting.models.municipality import Municipality
from composting.models.compost_density_register import CompostDensityRegister
from composting.tests.test_base import TestBase


class TestCompostDensityRegister(TestBase):
    def test_net_weight(self):
        compost_density = CompostDensityRegister(
            json_data={
                'filled_box_weight': '2.5',
                'empty_box_weight': '1.0'
            })
        self.assertEqual(compost_density.net_weight, 1.5)

    def test_density(self):
        municipality = Municipality(box_volume=0.125)
        compost_density = CompostDensityRegister(
            json_data={
                'filled_box_weight': '2.5',
                'empty_box_weight': '1.0'
            })
        self.assertEqual(compost_density.density(municipality), 12.0)


class TestCompostDensityRegisterWithTestData(TestBase):
    def setUp(self):
        super(TestCompostDensityRegisterWithTestData, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_get_by_date_returns_record_by_specified_date(self):
        compost_density = CompostDensityRegister.get_by_date(
            date(2014, 5, 1), self.municipality)
        self.assertIsInstance(compost_density, CompostDensityRegister)

    def test_get_by_date_returns_non_if_none_found(self):
        compost_density = CompostDensityRegister.get_by_date(
            date(2013, 1, 1),
            self.municipality)
        self.assertIsNone(compost_density)
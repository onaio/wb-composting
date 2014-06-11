import datetime

from composting.models.municipality import Municipality
from composting.models.compost_sales_register import CompostSalesRegister
from composting.models.compost_density_register import CompostDensityRegister
from composting.tests.test_base import TestBase


class TestCompostSalesRegister(TestBase):
    def test_volume_returns_none_if_bagged(self):
        compost_sale = CompostSalesRegister(
            json_data={
                'bagged_compost': 'yes'
            })
        self.assertIsNone(compost_sale.volume)

    def test_returns_volume_if_not_bagged(self):
        compost_sale = CompostSalesRegister(
            json_data={
                'bagged_compost': 'no',
                'compost_length': '3.0',
                'compost_width': '4.0',
                'compost_height': '5.0'
            })
        self.assertEqual(compost_sale.volume, 60.0)

    def test_get_compost_density(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        compost_sale = CompostSalesRegister(
            date=datetime.datetime(2014, 05, 01),
            json_data={
                'bagged_compost': 'no',
                'compost_length': '3.0',
                'compost_width': '4.0',
                'compost_height': '5.0'
            })
        compost_density = compost_sale.get_compost_density(municipality)
        self.assertIsInstance(compost_density, CompostDensityRegister)

    def test_get_compost_density_returns_none_if_no_density_record(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        compost_sale = CompostSalesRegister(
            date=datetime.datetime(2013, 01, 01),
            json_data={
                'bagged_compost': 'no',
                'compost_length': '3.0',
                'compost_width': '4.0',
                'compost_height': '5.0'
            })
        compost_density = compost_sale.get_compost_density(municipality)
        self.assertIsNone(compost_density)

    def test_weight_calculation(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        compost_sale = CompostSalesRegister(
            date=datetime.datetime(2014, 05, 01),
            json_data={
                'bagged_compost': 'no',
                'compost_length': '3.0',
                'compost_width': '4.0',
                'compost_height': '5.0'
            })
        weight = compost_sale.weight(municipality)
        self.assertAlmostEqual(weight, 864.0/1000)  # div to convert to tonnes

    def test_weight_calculation_returns_none_if_bagged(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        compost_sale = CompostSalesRegister(
            date=datetime.datetime(2013, 01, 01),
            json_data={
                'bagged_compost': 'yes',
            })
        weight = compost_sale.weight(municipality)
        self.assertIsNone(weight)

    def test_weight_calculation_returns_none_if_density_is_none(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        compost_sale = CompostSalesRegister(
            date=datetime.datetime(2013, 01, 01),
            json_data={
                'bagged_compost': 'no',
                'compost_length': '3.0',
                'compost_width': '4.0',
                'compost_height': '5.0'
            })
        weight = compost_sale.weight(municipality)
        self.assertIsNone(weight)
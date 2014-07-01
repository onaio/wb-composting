import datetime

from composting.models.municipality import Municipality
from composting.models.municipality_submission import MunicipalitySubmission
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
            },
            municipality_submission=MunicipalitySubmission(
                municipality=municipality))
        weight = compost_sale.weight()
        self.assertAlmostEqual(weight, 864.0/1000)  # div to convert to tonnes

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
            },
            municipality_submission=MunicipalitySubmission(
                municipality=municipality))
        weight = compost_sale.weight()
        self.assertIsNone(weight)

    def test_weight_calculation_returns_bagged_weight_if_bagged(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        compost_sale = CompostSalesRegister(
            date=datetime.datetime(2013, 01, 01),
            json_data={
                'bagged_compost': 'yes',
                'bagged_compost_weight': '1.5'
            },
            municipality_submission=MunicipalitySubmission(
                municipality=municipality))
        weight = compost_sale.weight()
        self.assertEqual(weight, 1.5)

    def test_create_or_update_report_raises_value_error_if_no_municipality(
            self):
        self.setup_test_data()
        compost_sale = CompostSalesRegister(
            date=datetime.datetime(2013, 01, 01),
            json_data={
                'bagged_compost': 'no',
                'compost_length': '3.0',
                'compost_width': '4.0',
                'compost_height': '5.0'
            })
        self.assertRaises(ValueError, compost_sale.create_or_update_report)

    def test_create_or_update_report(
            self):
        self.setup_test_data()
        compost_sale = CompostSalesRegister(
            date=datetime.datetime(2013, 01, 01),
            json_data={
                'bagged_compost': 'yes',
                'bagged_compost_weight': '1.5'
            })
        report = compost_sale.create_or_update_report()
        self.assertEqual(report.report_json, {
            'weight': 1.5
        })
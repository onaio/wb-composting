import datetime

from composting.tests.test_base import TestBase
from composting.models.municipality import Municipality
from composting.models.monthly_rejects_density import MonthlyRejectsDensity
from composting.models.municipality_submission import MunicipalitySubmission


class TestMonthlyRejectsDensity(TestBase):
    def setUp(self):
        super(TestMonthlyRejectsDensity, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_net_weight(self):
        monthly_reject_density = MonthlyRejectsDensity(
            json_data={
                'filled_box_weight': '48',
                'empty_box_weight': '16'
            })
        self.assertEqual(monthly_reject_density.net_weight, 32.0)

    def test_density(self):
        monthly_reject_density = MonthlyRejectsDensity(
            json_data={
                'filled_box_weight': '48',
                'empty_box_weight': '16'
            })
        density = monthly_reject_density.density(self.municipality)
        self.assertEqual(density, 256.0)
from datetime import date

from composting.models.monthly_rejects_composition import\
    MonthlyRejectsComposition
from composting.models.municipality import Municipality
from composting.tests.test_base import TestBase


class TestMonthlyRejectsComposition(TestBase):
    def setUp(self):
        super(TestMonthlyRejectsComposition, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_total_mature_compost_volume(self):
        monthly_rejects_composition = MonthlyRejectsComposition(
            date=date(2014, 5, 1),
            json_data={
                'total_mature_compost': '200'
            }
        )
        # V = M/D;
        # M = 200.0;
        # Avg. D -> D = 2.8 - 1.0 = 1.8; V = 0.125m3; 1.8/0.125 = 14.4 kg/m3
        # V = 200.0/14.4 = 13.8888
        self.assertAlmostEqual(
            monthly_rejects_composition.total_mature_compost_volume(
                self.municipality), 13.888888889)
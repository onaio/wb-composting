import transaction

from datetime import date

from composting.models.base import DBSession
from composting.models.submission import Submission
from composting.models.monthly_rejects_composition import\
    MonthlyRejectsComposition
from composting.models.compost_density_register import CompostDensityRegister
from composting.models.municipality import Municipality
from composting.tests.test_base import TestBase


class TestMonthlyRejectsComposition(TestBase):
    def setUp(self):
        super(TestMonthlyRejectsComposition, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def setup_monthly_compost_density(self):
        # get the monthly density record and approve if
        compost_density = CompostDensityRegister.get(
            CompostDensityRegister.date == date(2014, 5, 1))
        compost_density.status = Submission.APPROVED
        with transaction.manager:
            DBSession.add(compost_density)

    def test_volume_of_mature_compost(self):
        self.setup_monthly_compost_density()
        monthly_rejects_composition = MonthlyRejectsComposition.get(
            MonthlyRejectsComposition.date == date(2014, 5, 1))
        # V = M/D;
        # M = 60.0;
        # Avg. D -> D = 2.8 - 1.0 = 1.8; V = 0.125m3; 1.8/0.125 = 14.4 kg/m3
        # V = 60.0/14.4 = 4.1666666667
        self.assertAlmostEqual(
            monthly_rejects_composition.volume_of_mature_compost(),
            4.1666666667)

    def test_create_or_update_report(self):
        self.setup_monthly_compost_density()
        monthly_rejects_composition = MonthlyRejectsComposition.get(
            MonthlyRejectsComposition.date == date(2014, 5, 1))
        report = monthly_rejects_composition.create_or_update_report()
import datetime

from composting.models.base import DBSession
from composting.models import Municipality
from composting.models.submission import Submission
from composting.models.daily_waste import DailyWaste
from composting.models.monthly_density import MonthlyDensity
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.report import Report
from composting.tests.test_base import IntegrationTestBase


class TestMunicipality(IntegrationTestBase):
    def test_update(self):
        m = Municipality(name="Test Municipal", box_volume=0.125,
                         wheelbarrow_volume=0.625, leachete_tank_length=5.0,
                         leachete_tank_width=5.0)
        m.update(name="Another Test Municipal", box_volume=0.3,
                 wheelbarrow_volume=0.15, leachete_tank_length=8.0,
                 leachete_tank_width=6.0)
        self.assertEqual(m.name, "Another Test Municipal")
        self.assertEqual(m.box_volume, 0.3)
        self.assertEqual(m.wheelbarrow_volume, 0.15)
        self.assertEqual(m.leachete_tank_length, 8.0)
        self.assertEqual(m.leachete_tank_width, 6.0)

    def test_num_daily_wastes_returns_cached_count_if_set(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        municipality._num_actionable_daily_wastes = 1000
        self.assertEqual(municipality.num_actionable_daily_wastes, 1000)

    def test_num_daily_wastes_returns_actual_count_if_not_cached(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        self.assertEqual(municipality.num_actionable_daily_wastes, 1)

    def test_num_monthly_density_returns_cached_count_if_set(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        municipality._num_actionable_monthly_waste = 10
        self.assertEqual(municipality.num_actionable_monthly_waste, 10)

    def test_num_monthly_density_returns_actual_count_if_not_cached(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        self.assertEqual(municipality.num_actionable_monthly_waste, 3)

    def test_num_trucks_delivered_msw(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        # approve some daily wastes to have data to aggregate on
        num_reports = Report.count()
        daily_wastes = DBSession\
            .query(DailyWaste)\
            .join(MunicipalitySubmission)\
            .filter(DailyWaste.status == Submission.PENDING).all()
        for daily_waste in daily_wastes:
            daily_waste.status = Submission.APPROVED
        # check that we've incremented num reports buy number of approved
        # submissions
        self.assertEqual(Report.count(), num_reports + len(daily_wastes))
        start = datetime.date(2014, 4, 1)
        end = datetime.date(2014, 4, 30)
        num_trucks = municipality.num_trucks_delivered_msw(start, end)
        self.assertEqual(num_trucks, 1)
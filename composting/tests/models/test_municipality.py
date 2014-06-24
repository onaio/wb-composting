import datetime

from composting.models.base import DBSession
from composting.models import Municipality
from composting.models.submission import Submission
from composting.models.daily_waste import DailyWaste
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.report import Report

from composting.tests.test_base import TestBase, IntegrationTestBase


class TestMunicipality(TestBase):
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


class TestMunicipalityIntegration(IntegrationTestBase):
    def setUp(self):
        super(TestMunicipalityIntegration, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_num_daily_wastes_returns_cached_count_if_set(self):
        self.municipality._num_actionable_daily_wastes = 1000
        self.assertEqual(self.municipality.num_actionable_daily_wastes, 1000)

    def test_num_daily_wastes_returns_actual_count_if_not_cached(self):
        self.assertEqual(self.municipality.num_actionable_daily_wastes, 2)

    def test_num_monthly_density_returns_cached_count_if_set(self):
        self.municipality._num_actionable_monthly_waste = 10
        self.assertEqual(self.municipality.num_actionable_monthly_waste, 10)

    def test_num_monthly_density_returns_actual_count_if_not_cached(self):
        self.assertEqual(self.municipality.num_actionable_monthly_waste, 3)

    def populate_daily_waste_reports(self):
        daily_wastes = DBSession\
            .query(DailyWaste)\
            .join(MunicipalitySubmission)\
            .filter(DailyWaste.status == Submission.PENDING).all()

        for daily_waste in daily_wastes:
            daily_waste.status = Submission.APPROVED

        return daily_wastes

    def populate_monthly_density_reports(self):
        # Should be run before daily wastes to make sure daily wastes have a
        # density to reference
        pass

    def test_num_trucks_delivered_msw(self):
        # approve some daily wastes to have data to aggregate on
        num_reports = Report.count()
        daily_wastes = self.populate_daily_waste_reports()

        # check that we've incremented num reports buy number of approved
        # submissions
        self.assertEqual(Report.count(), num_reports + len(daily_wastes))
        start = datetime.date(2014, 4, 1)
        end = datetime.date(2014, 4, 30)
        num_trucks = self.municipality.num_trucks_delivered_msw(start, end)
        self.assertEqual(num_trucks, 2)

    def test_density_of_msw(self):
        pass

    def test_volume_of_msw_processed(self):
        self.populate_monthly_density_reports()
        self.municipality.volume_of_msw_processed()
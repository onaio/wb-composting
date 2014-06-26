import datetime
import transaction

from composting.models.base import DBSession
from composting.models import Municipality
from composting.models.submission import Submission
from composting.models.daily_waste import DailyWaste
from composting.models.monthly_density import MonthlyDensity
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.report import Report
from composting.models.skip import Skip

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
        # approve some daily wastes to have data to aggregate on
        num_reports = Report.count()
        daily_wastes = DBSession\
            .query(DailyWaste)\
            .join(MunicipalitySubmission)\
            .filter(DailyWaste.status == Submission.PENDING)\
            .all()

        for daily_waste in daily_wastes:
            daily_waste.status = Submission.APPROVED

        # check that we've incremented num reports buy number of approved
        # submissions
        self.assertEqual(Report.count(), num_reports + len(daily_wastes))

        return daily_wastes

    def populate_monthly_density_reports(self):
        # Should be run before daily wastes to make sure daily wastes have a
        # density to reference

        # approve monthly density records to have data to aggregate on
        query = DBSession\
            .query(MonthlyDensity)\
            .join(MunicipalitySubmission)\
            .filter(MonthlyDensity.status == Submission.PENDING)
        monthly_densities = query.all()

        # change the monthly density threshold to
        MonthlyDensity.THRESHOLD_MIN = 3

        for monthly_density in monthly_densities:
            monthly_density.status = Submission.APPROVED

        with transaction.manager:
            DBSession.add_all(monthly_densities)

        # check that our number of approved monthly densities
        self.assertEqual(query.count(), 0)

        return monthly_densities

    def test_num_trucks_delivered_msw(self):
        self.populate_daily_waste_reports()
        start = datetime.date(2014, 4, 1)
        end = datetime.date(2014, 4, 30)
        num_trucks = self.municipality.num_trucks_delivered_msw(start, end)
        self.assertEqual(num_trucks, 2)

    def test_density_of_msw(self):
        self.populate_monthly_density_reports()
        start = datetime.date(2014, 4, 1)
        end = datetime.date(2014, 4, 30)
        self.populate_daily_waste_reports()
        average_density = self.municipality.density_of_msw(start, end)
        self.assertAlmostEqual(average_density, 0.000202564)

    def test_volume_of_msw_processed(self):
        self.populate_monthly_density_reports()
        start = datetime.date(2014, 4, 1)
        end = datetime.date(2014, 4, 30)
        self.populate_daily_waste_reports()
        total_volume = self.municipality.volume_of_msw_processed(start, end)
        self.assertAlmostEqual(total_volume, 178750.0)

    def test_tonnage_of_msw_processed(self):
        self.populate_monthly_density_reports()
        start = datetime.date(2014, 4, 1)
        end = datetime.date(2014, 4, 30)
        self.populate_daily_waste_reports()
        total_tonnage = self.municipality.tonnage_of_msw_processed(start, end)
        self.assertAlmostEqual(total_tonnage, 36.2083333333333)

    def test_get_skip_if_skip_not_in_cache(self):
        skip = self.municipality.get_skip('A')
        self.assertIsInstance(skip, Skip)

    def test_get_skip_returns_cached_skip(self):
        skip = Skip(skip_type='X')
        self.municipality._skips['X'] = skip
        self.assertEqual(self.municipality.get_skip('X'), skip)

    def test_get_skip_returns_none_if_skip_doesnt_exist(self):
        self.assertIsNone(self.municipality.get_skip('Z'))
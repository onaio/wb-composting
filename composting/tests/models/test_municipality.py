import datetime
import transaction

from composting.models.base import DBSession
from composting.models import Municipality
from composting.models.submission import Submission
from composting.models.daily_waste import DailyWaste
from composting.models.daily_vehicle_register import DailyVehicleDataRegister
from composting.models.compost_density_register import CompostDensityRegister
from composting.models.compost_sales_register import CompostSalesRegister
from composting.models.windrow_monitoring import WindrowMonitoring
from composting.models.monthly_density import MonthlyDensity
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.electricity_register import ElectricityRegister
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

    def get_pending_submissions_by_class(self, klass):
        pending_submissions_query = DBSession\
            .query(klass)\
            .join(MunicipalitySubmission)\
            .filter(klass.status == Submission.PENDING)
        return pending_submissions_query

    def populate_daily_waste_reports(self):
        # approve some daily wastes to have data to aggregate on
        num_reports = Report.count()
        daily_wastes = self.get_pending_submissions_by_class(DailyWaste).all()

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
        query = self.get_pending_submissions_by_class(MonthlyDensity)
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

    def populate_compost_density(self):
        # Should be run before compost sales to make sure compost sales have a
        # density to reference

        # approve compost density records to have data to aggregate on
        query = self.get_pending_submissions_by_class(CompostDensityRegister)
        compost_densities = query.all()

        for compost_density in compost_densities:
            compost_density.status = Submission.APPROVED

        with transaction.manager:
            DBSession.add_all(compost_densities)

        # check that our number of un-approved compost densities
        self.assertEqual(query.count(), 0)

        return compost_densities

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

    def populate_daily_vehicle_data_register_reports(self):
        query = self.get_pending_submissions_by_class(DailyVehicleDataRegister)
        daily_vehicle_registers = query.all()

        for daily_vehicle_register in daily_vehicle_registers:
            daily_vehicle_register.status = Submission.APPROVED

        with transaction.manager:
            DBSession.add_all(daily_vehicle_registers)

        self.assertEqual(query.count(), 0)

    def test_fuel_consumption(self):
        self.populate_daily_vehicle_data_register_reports()
        start = datetime.date(2014, 6, 1)
        end = datetime.date(2014, 6, 30)
        fuel_consumption = self.municipality.fuel_consumption(start, end)
        self.assertEqual(fuel_consumption, 18.6)

    def test_count_of_vehicles_transporting_compost(self):
        start = datetime.date(2014, 5, 1)
        end = datetime.date(2014, 6, 30)

        vehicle_count = self.municipality.vehicle_count(start, end)
        self.assertEqual(vehicle_count, 0)
        self.populate_compost_density()
        self.populate_compost_sales_register()

        self.municipality = Municipality.get(Municipality.name == "Mukono")
        vehicle_count = self.municipality.vehicle_count(start, end)
        self.assertEqual(vehicle_count, 2)

    def test_quantity_of_compost_sold(self):
        self.populate_compost_density()
        self.populate_compost_sales_register()

        self.municipality = Municipality.get(Municipality.name == "Mukono")
        start = datetime.date(2014, 5, 1)
        end = datetime.date(2014, 6, 30)
        self.assertAlmostEqual(
            self.municipality.quantity_of_compost_sold(start, end),
            1.38576)

    def test_get_skip_if_skip_not_in_cache(self):
        skip = self.municipality.get_skip('A')
        self.assertIsInstance(skip, Skip)

    def test_get_skip_returns_cached_skip(self):
        skip = Skip(skip_type='X')
        self.municipality._skips['X'] = skip
        self.assertEqual(self.municipality.get_skip('X'), skip)

    def test_get_skip_returns_none_if_skip_doesnt_exist(self):
        self.assertIsNone(self.municipality.get_skip('Z'))

    def test_volume_of_mature_compost(self):
        # we already have a monthly mature compost record for May within
        # tests, lets add another for june to test with
        pass

    def populate_compost_sales_register(self):
        query = self.get_pending_submissions_by_class(CompostSalesRegister)
        compost_sales_registers = query.all()

        for compost_sales_register in compost_sales_registers:
            compost_sales_register.status = Submission.APPROVED

        self.assertEqual(query.count(), 0)

    def test_average_distance_travelled(self):
        start = datetime.date(2014, 5, 1)
        end = datetime.date(2014, 6, 30)

        self.populate_compost_density()
        self.populate_compost_sales_register()
        distance = self.municipality.average_distance_travelled(start, end)

        self.assertEqual(distance, 13.25)

    def populate_windrow_monistoring(self):
        query = self.get_pending_submissions_by_class(WindrowMonitoring)
        windrow_submissions = query.all()

        for windrow_submission in windrow_submissions:
            windrow_submission.status = Submission.APPROVED

        self.assertEqual(query.count(), 0)

    def test_windrow_sample_number(self):
        start = datetime.date(2014, 6, 1)
        end = datetime.date(2014, 6, 30)

        total_windrow_samples = self.municipality.total_windrow_samples(
            start, end)
        self.assertEqual(total_windrow_samples, 0)

        self.populate_windrow_monistoring()

        total_windrow_samples = self.municipality.total_windrow_samples(
            start, end)
        self.assertEqual(total_windrow_samples, 10)

    def test_low_windrow_sample_count(self):
        start = datetime.date(2014, 6, 1)
        end = datetime.date(2014, 6, 30)

        count = self.municipality.low_windrow_sample_count(start, end)
        self.assertIsNone(count)

        self.populate_windrow_monistoring()

        count = self.municipality.low_windrow_sample_count(start, end)
        self.assertEqual(count, 3)

    def test_percentage_of_low_samples(self):
        start = datetime.date(2014, 6, 1)
        end = datetime.date(2014, 6, 30)

        self.populate_windrow_monistoring()

        percentage = self.municipality.percentage_of_low_samples(start, end)
        self.assertAlmostEqual(percentage, 0.3)

    def populate_electricity_register_reports(self):
        query = self.get_pending_submissions_by_class(ElectricityRegister)
        electricity_registers = query.all()

        for electricity_register in electricity_registers:
            electricity_register.status = Submission.APPROVED

        self.assertEqual(query.count(), 0)

    def test_electricity_consumption_calculation(self):
        start = datetime.date(2014, 5, 1)
        end = datetime.date(2014, 5, 30)

        self.populate_electricity_register_reports()
        consumption = self.municipality.electricity_consumption(start, end)
        self.assertEqual(consumption, 351)

    def test_electricity_consumption_calculation_for_first_register(self):
        start = datetime.date(2014, 4, 1)
        end = datetime.date(2014, 4, 30)

        self.populate_electricity_register_reports()
        consumption = self.municipality.electricity_consumption(start, end)
        self.assertIsNone(consumption)

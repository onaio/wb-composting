import datetime

from composting.tests.test_base import TestBase
from composting.models.municipality import Municipality
from composting.models.monthly_density import MonthlyDensity
from composting.models.municipality_submission import MunicipalitySubmission


class TestMonthlyDensity(TestBase):
    def setUp(self):
        super(TestMonthlyDensity, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_volume_when_compressor(self):
        monthly_density = MonthlyDensity(json_data={
            MonthlyDensity.COMPRESSOR_TRUCK_FIELD: 'yes',
            MonthlyDensity.VOLUME_FIELD: '20.0'
        })
        self.assertEqual(monthly_density.volume, 20.0)

    def test_volume_when_not_compressor(self):
        monthly_density = MonthlyDensity(
            json_data={
                MonthlyDensity.COMPRESSOR_TRUCK_FIELD: 'no',
                MonthlyDensity.SKIP_TYPE_FIELD: 'A',
                MonthlyDensity.WASTE_HEIGHT_FIELD: '20.0'
            },
            municipality_submission=MunicipalitySubmission(
                municipality=self.municipality
            ))
        self.assertEqual(monthly_density.volume, 6500.0)

    def test_volume_returns_none_if_skip_not_found(self):
        monthly_density = MonthlyDensity(
            json_data={
                MonthlyDensity.COMPRESSOR_TRUCK_FIELD: 'no',
                MonthlyDensity.SKIP_TYPE_FIELD: 'Z',
                MonthlyDensity.WASTE_HEIGHT_FIELD: '20.0'
            },
            municipality_submission=MunicipalitySubmission(
                municipality=self.municipality
            ))
        self.assertIsNone(monthly_density.volume)

    def test_net_weight(self):
        monthly_density = MonthlyDensity(json_data={
            MonthlyDensity.FILLED_WEIGHT_FIELD: '20',
            MonthlyDensity.EMPTY_WEIGHT_FIELD: '12'
        })
        self.assertEqual(monthly_density.net_weight, 8.0)

    def test_density(self):
        monthly_density = MonthlyDensity(json_data={
            MonthlyDensity.COMPRESSOR_TRUCK_FIELD: 'yes',
            MonthlyDensity.FILLED_WEIGHT_FIELD: '20',
            MonthlyDensity.EMPTY_WEIGHT_FIELD: '12',
            MonthlyDensity.VOLUME_FIELD: '20.0'
        })
        self.assertEqual(monthly_density.density, 0.4)

    def test_calculate_average_density(self):
        average_density = MonthlyDensity.calculate_average_density([
            MonthlyDensity(json_data={
                MonthlyDensity.COMPRESSOR_TRUCK_FIELD: 'yes',
                MonthlyDensity.FILLED_WEIGHT_FIELD: '20',
                MonthlyDensity.EMPTY_WEIGHT_FIELD: '12',
                MonthlyDensity.VOLUME_FIELD: '20.0'
            }),
            # density = 0.8
            MonthlyDensity(json_data={
                MonthlyDensity.COMPRESSOR_TRUCK_FIELD: 'yes',
                MonthlyDensity.FILLED_WEIGHT_FIELD: '20',
                MonthlyDensity.EMPTY_WEIGHT_FIELD: '12',
                MonthlyDensity.VOLUME_FIELD: '10.0'
            })
            # density = 0.4
        ])
        self.assertAlmostEqual(average_density, 0.6)

    def test_get_average_density_returns_none_if_below_threshold(self):
        # this also checks that PENDING and REJECTED submissions are not
        # considered
        date = datetime.date(2014, 05, 07)
        average_density = MonthlyDensity.get_average_density(date)
        self.assertIsNone(average_density)

    def test_get_average_density_returns_avg_if_above_threshold(self):
        MonthlyDensity.THRESHOLD_MIN = 2
        date = datetime.date(2014, 04, 07)
        average_density = MonthlyDensity.get_average_density(date)
        self.assertAlmostEqual(average_density, 0.000226923)
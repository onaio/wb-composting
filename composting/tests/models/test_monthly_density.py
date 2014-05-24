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
                municipality_id=self.municipality.id
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
                municipality_id=self.municipality.id
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

    def test_get_average_density(self):
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
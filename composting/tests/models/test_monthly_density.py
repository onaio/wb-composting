from composting.tests.test_base import TestBase

from composting.models.monthly_density import MonthlyDensity


class TestMonthlyDensity(TestBase):
    def setUp(self):
        super(TestMonthlyDensity, self).setUp()
        self.setup_test_data()

    def test_volume_when_compressor(self):
        monthly_density = MonthlyDensity(json_data={
            MonthlyDensity.COMPRESSOR_TRUCK_FIELD: 'yes',
            MonthlyDensity.VOLUME_FIELD: '20.0'
        })
        self.assertEqual(monthly_density.volume, 20.0)

    def test_volume_when_not_compressor(self):
        monthly_density = MonthlyDensity(json_data={
            MonthlyDensity.COMPRESSOR_TRUCK_FIELD: 'no',
            MonthlyDensity.SKIP_TYPE_FIELD: 'A',
            MonthlyDensity.WASTE_HEIGHT_FIELD: '20.0'
        })
        self.assertEqual(monthly_density.volume, 6500.0)

    def test_volume_returns_none_if_skip_not_found(self):
        monthly_density = MonthlyDensity(json_data={
            MonthlyDensity.COMPRESSOR_TRUCK_FIELD: 'no',
            MonthlyDensity.SKIP_TYPE_FIELD: 'Z',
            MonthlyDensity.WASTE_HEIGHT_FIELD: '20.0'
        })
        self.assertIsNone(monthly_density.volume)
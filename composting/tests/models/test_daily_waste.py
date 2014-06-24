from sqlalchemy.orm.exc import NoResultFound

from composting.tests.test_base import TestBase, DBSession
from composting.models import (
    DailyWaste, Skip, Municipality, Submission)
from composting.models.municipality_submission import MunicipalitySubmission


class TestDailyWaste(TestBase):

    def setUp(self):
        super(TestDailyWaste, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_volume_returns_raw_value_if_compressor(self):
        daily_waste = DailyWaste(
            json_data={
                'compressor_truck': 'yes',
                'volume': '20.0',
                'skip_type': 'A'
            })
        self.assertEqual(daily_waste.volume, 20.0)

    def test_calculates_volume_if_not_compressor(self):
        municipality_submission = MunicipalitySubmission(
            municipality_id=self.municipality.id)
        daily_waste = DailyWaste(
            json_data={
                'compressor_truck': 'no',
                'waste_height': '20.0',
                'skip_type': 'A'  # has a cross sectional area of 325
            }, municipality_submission=municipality_submission)
        self.assertEqual(daily_waste.volume, 6500.0)

    def test_volume_returns_none_if_no_skip(self):
        municipality_submission = MunicipalitySubmission(
            municipality=self.municipality)
        daily_waste = DailyWaste(
            json_data={
                'compressor_truck': 'no',
                'waste_height': '20.0',
                'skip_type': 'F'
            }, municipality_submission=municipality_submission)
        self.assertIsNone(daily_waste.volume)

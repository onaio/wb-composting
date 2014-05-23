from sqlalchemy.orm.exc import NoResultFound

from composting.tests.test_base import TestBase, DBSession
from composting.models import (
    DailyWaste, Skip, Municipality, Submission)
from composting.models.municipality_submission import MunicipalitySubmission


class TestDailyWaste(TestBase):
    def setUp(self):
        super(TestDailyWaste, self).setUp()
        self.setup_test_data()

    def test_skip_returns_skip_if_found(self):
        daily_waste = DBSession.query(DailyWaste)\
            .filter(DailyWaste.json_data['skip_type'].astext == 'A')\
            .first()
        skip = daily_waste.get_skip()
        self.assertIsInstance(skip, Skip)

    def test_skip_raises_no_result_if_not_found(self):
        daily_waste = DBSession.query(DailyWaste)\
            .filter(DailyWaste.json_data['skip_type'].astext == 'F')\
            .first()
        self.assertRaises(NoResultFound, daily_waste.get_skip)

    def test_volume_returns_raw_value_if_compressor(self):
        daily_waste = DailyWaste(
            json_data={
                'compressor_truck': 'yes',
                'volume': '20.0',
                'skip_type': 'A'
            })
        self.assertEqual(daily_waste.volume, 20.0)

    def test_calculates_volume_if_not_compressor(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        municipality_submission = MunicipalitySubmission(
            municipality=municipality)
        daily_waste = DailyWaste(
            json_data={
                'compressor_truck': 'no',
                'waste_height': '20.0',
                'skip_type': 'A'  # has a cross sectional area of 325
            }, municipality_submission=municipality_submission)
        self.assertEqual(daily_waste.volume, 6500.0)

    def test_volume_returns_none_if_no_skip(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        municipality_submission = MunicipalitySubmission(
            municipality=municipality)
        daily_waste = DailyWaste(
            json_data={
                'compressor_truck': 'no',
                'waste_height': '20.0',
                'skip_type': 'F'
            }, municipality_submission=municipality_submission)
        self.assertIsNone(daily_waste.volume)
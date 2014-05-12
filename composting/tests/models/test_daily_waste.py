from sqlalchemy.orm.exc import NoResultFound

from composting.tests.test_base import TestBase
from composting.models import (
    DailyWaste, Skip, Municipality, Submission)


class TestDailyWaste(TestBase):
    def test_skip_returns_skip_if_found(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        submission = Submission(
            json_data={
                'skip_type': 'A'
            })
        daily_waste = DailyWaste(
            submission=submission, municipality_id=municipality.id)
        self.assertIsInstance(daily_waste.get_skip(), Skip)

    def test_skip_raises_no_result_if_not_found(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        submission = Submission(
            json_data={
                'skip_type': 'Z'
            })
        daily_waste = DailyWaste(
            submission=submission, municipality_id=municipality.id)
        self.assertRaises(NoResultFound, daily_waste.get_skip)

    def test_volume_returns_raw_value_if_compressor(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        submission = Submission(
            json_data={
                'compressor_truck': 'yes',
                'volume': '20.0',
                'skip_type': 'A'
            })
        daily_waste = DailyWaste(
            submission=submission, municipality_id=municipality.id)
        self.assertEqual(daily_waste.volume, 20.0)

    def test_calculates_volume_if_not_compressor(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        submission = Submission(
            json_data={
                'compressor_truck': 'no',
                'waste_height': '20.0',
                'skip_type': 'A'  # has a cross sectional area of 325
            })
        daily_waste = DailyWaste(
            submission=submission, municipality_id=municipality.id)
        self.assertEqual(daily_waste.volume, 6500.0)

    def test_volume_returns_none_if_no_skip(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        submission = Submission(
            json_data={
                'compressor_truck': 'no',
                'waste_height': '20.0',
                'skip_type': 'Z'  # has a cross sectional area of 325
            })
        daily_waste = DailyWaste(
            submission=submission, municipality_id=municipality.id)
        self.assertIsNone(daily_waste.volume)
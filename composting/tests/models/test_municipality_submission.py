from sqlalchemy.orm.exc import NoResultFound

from composting.models.municipality import Municipality
from composting.models.daily_waste import DailyWaste
from composting.models.skip import Skip
from composting.models.municipality_submission import MunicipalitySubmission
from composting.tests.test_base import TestBase


class TestMunicipalitySubmission(TestBase):
    def setUp(self):
        super(TestMunicipalitySubmission, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_get_items_on_daily_waste(self):
        items = MunicipalitySubmission.get_items(self.municipality, DailyWaste)
        daily_wastes = self.get_submissions_by_xform_id(
            DailyWaste.XFORM_ID)
        self.assertEqual(len(items), len(daily_wastes))

    def test_get_skip(self):
        municipality_submission = MunicipalitySubmission(
            municipality=self.municipality)
        skip = municipality_submission.get_skip('A')
        self.assertIsInstance(skip, Skip)

    def test_get_skip_raises_no_result_found_if_skip_not_found(self):
        municipality_submission = MunicipalitySubmission(
            municipality=self.municipality)
        self.assertRaises(NoResultFound, municipality_submission.get_skip, 'Z')
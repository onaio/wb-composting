from composting import constants
from composting.models.municipality import Municipality
from composting.models.daily_waste import DailyWaste
from composting.models.municipality_submission import MunicipalitySubmission
from composting.tests.test_base import TestBase


class TestMunicipalitySubmission(TestBase):
    def setUp(self):
        super(TestMunicipalitySubmission, self).setUp()
        self.setup_test_data()

    def test_get_items_on_daily_waste(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        items = MunicipalitySubmission.get_items(municipality, DailyWaste)
        daily_wastes = self.get_submissions_by_xform_id(
            constants.DAILY_WASTE_REGISTER_FORM)
        self.assertEqual(len(items), len(daily_wastes))

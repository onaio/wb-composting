from pyramid import testing

from composting.tests.test_base import IntegrationTestBase
from composting.models import Municipality, DailyWaste, Submission


class TestMunicipality(IntegrationTestBase):
    def test_test_get_register_records_with_criterion(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        results = municipality.get_register_records(
            DailyWaste, Submission.status == Submission.PENDING)
        self.assertEqual(len(results), 1)

    def test_get_register_records_on_daily_waste(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        results = municipality.get_register_records(DailyWaste)
        self.assertTrue(all([isinstance(r, DailyWaste) for r in results]))
        self.assertEqual(len(results), 2)
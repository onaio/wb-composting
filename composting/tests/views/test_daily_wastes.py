from composting.tests.test_base import FunctionalTestBase
from composting.models import DailyWaste


class TestDailyWastesFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestDailyWastesFunctional, self).setUp()
        self.setup_test_data()

    def test_show(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'daily-waste', traverse=(daily_waste.id,))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)
from composting.models import Municipality
from composting.tests.test_base import FunctionalTestBase


class TestSubmissionsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestSubmissionsFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_list_for_monthly_density(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'monthly-waste-density'))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)
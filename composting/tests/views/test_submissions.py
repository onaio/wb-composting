from composting.models import Municipality, Submission
from composting.views.submissions import Submissions
from composting.tests.test_base import IntegrationTestBase, FunctionalTestBase


class TestSubmissions(IntegrationTestBase):
    def setUp(self):
        super(TestSubmissions, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")
        self.municipality.request = self.request

    def test_daily_waste_list(self):
        daily_waste = self.municipality['daily-waste']
        self.request.context = daily_waste
        view = Submissions(self.request).list
        result = view()
        self.assertEqual(sorted(result.keys()),
                         sorted(['municipality', 'items', 'statuses']))


class TestSubmissionsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestSubmissionsFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_daily_waste_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'daily-waste'),
            _query={Submission.PENDING: '1', Submission.REJECTED: '1'})
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
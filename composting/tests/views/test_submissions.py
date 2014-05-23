from webob.multidict import MultiDict
from pyramid.response import Response

from composting.models import Municipality, Submission
from composting.models.daily_waste import DailyWaste
from composting.views.submissions import Submissions
from composting.tests.test_base import IntegrationTestBase, FunctionalTestBase


class TestSubmissions(IntegrationTestBase):
    def setUp(self):
        super(TestSubmissions, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")
        self.municipality.request = self.request
        self.views = Submissions(self.request)

    def test_daily_waste_list(self):
        daily_waste = self.municipality['daily-waste']
        self.request.context = daily_waste
        result = self.views.list()
        self.assertEqual(sorted(result.keys()),
                         sorted(['municipality', 'items', 'statuses']))

    def test_approve(self):
        result = self.views.approve()
        self.assertIsInstance(result, Response)
        self.assertEqual(self.request.new_status, Submission.APPROVED)
        self.assertEqual(self.request.action, 'daily-waste')

    def test_reject(self):
        result = self.views.reject()
        self.assertIsInstance(result, Response)
        self.assertEqual(self.request.new_status, Submission.REJECTED)
        self.assertEqual(self.request.action, 'daily-waste')

    def test_unapprove(self):
        result = self.views.unapprove()
        self.assertIsInstance(result, Response)
        self.assertEqual(self.request.new_status, Submission.PENDING)
        self.assertEqual(self.request.action, 'daily-waste')


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

    def test_approve_daily_waste(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_waste.id, 'approve'))
        response = self.testapp.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url(
                'municipalities',
                traverse=(self.municipality.id, 'daily-waste')))

    def test_reject_daily_waste(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_waste.id, 'reject'))
        response = self.testapp.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url(
                'municipalities',
                traverse=(self.municipality.id, 'daily-waste')))

    def test_unapprove_daily_waste(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_waste.id, 'unapprove'))
        response = self.testapp.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url(
                'municipalities',
                traverse=(self.municipality.id, 'daily-waste')))
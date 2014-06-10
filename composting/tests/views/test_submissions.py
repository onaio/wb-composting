from webob.multidict import MultiDict
from pyramid.response import Response

from composting.models import Municipality, Submission
from composting.models.daily_waste import DailyWaste
from composting.models.monthly_density import MonthlyDensity
from composting.models.monthly_waste_composition import MonthlyWasteComposition
from composting.models.windrow_monitoring import WindrowMonitoring
from composting.models.daily_rejects_landfilled import DailyRejectsLandfilled
from composting.models.monthly_rejects_density import MonthlyRejectsDensity
from composting.models.electricity_register import ElectricityRegister
from composting.models.leachete_monthly_register import LeacheteMonthlyRegister
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

    def test_reject(self):
        result = self.views.reject()
        self.assertIsInstance(result, Response)
        self.assertEqual(self.request.new_status, Submission.REJECTED)

    def test_unapprove(self):
        result = self.views.unapprove()
        self.assertIsInstance(result, Response)
        self.assertEqual(self.request.new_status, Submission.PENDING)


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

    def test_daily_waste_show(self):
        monthly_density = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(monthly_density.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def assertActionMatches(self, location, action):
        self.assertEqual(
            location,
            self.request.route_url(
                'municipalities',
                traverse=(self.municipality.id, action)))

    def test_approve_daily_waste(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_waste.id, 'approve'))
        response = self.testapp.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertActionMatches(response.location, 'daily-waste')
        response.follow()

    def test_reject_daily_waste(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_waste.id, 'reject'))
        response = self.testapp.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertActionMatches(response.location, 'daily-waste')
        response.follow()

    def test_unapprove_daily_waste(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_waste.id, 'unapprove'))
        response = self.testapp.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertActionMatches(response.location, 'daily-waste')
        response.follow()

    def test_approve_monthly_waste_density(self):
        monthly_density = MonthlyDensity.newest()
        url = self.request.route_path(
            'submissions', traverse=(monthly_density.id, 'approve'))
        response = self.testapp.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertActionMatches(response.location, 'monthly-waste-density')
        response.follow()

    def test_monthly_waste_composition_show(self):
        monthly_waste = MonthlyWasteComposition.newest()
        url = self.request.route_path(
            'submissions', traverse=(monthly_waste.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_windrow_monitoring_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'windrow-monitoring'),
            _query={Submission.PENDING: '1', Submission.REJECTED: '1'})
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_windrow_monitoring_show(self):
        monthly_waste = WindrowMonitoring.newest()
        url = self.request.route_path(
            'submissions', traverse=(monthly_waste.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_daily_rejects_landfilled_show(self):
        daily_reject = DailyRejectsLandfilled.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_reject.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_density_of_rejects_from_sieving_show(self):
        rejects_density = MonthlyRejectsDensity.newest()
        url = self.request.route_path(
            'submissions', traverse=(rejects_density.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_municipality_electricity_register_show(self):
        electricity_register = ElectricityRegister.newest()
        url = self.request.route_path(
            'submissions', traverse=(electricity_register.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_leachete_monthly_register_show(self):
        electricity_register = LeacheteMonthlyRegister.newest()
        url = self.request.route_path(
            'submissions', traverse=(electricity_register.id,))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
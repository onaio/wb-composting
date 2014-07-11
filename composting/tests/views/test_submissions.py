from pyramid.response import Response
from httmock import urlmatch, HTTMock

from composting.models import Municipality, Submission
from composting.models.daily_waste import DailyWaste
from composting.models.monthly_waste_composition import MonthlyWasteComposition
from composting.models.windrow_monitoring import WindrowMonitoring
from composting.models.daily_rejects_landfilled import DailyRejectsLandfilled
from composting.models.monthly_rejects_density import MonthlyRejectsDensity
from composting.models.electricity_register import ElectricityRegister
from composting.models.leachete_monthly_register import LeacheteMonthlyRegister
from composting.models.compost_sales_register import CompostSalesRegister
from composting.models.compost_density_register import CompostDensityRegister
from composting.models.monthly_rejects_composition import (
    MonthlyRejectsComposition)
from composting.models.daily_vehicle_register import DailyVehicleDataRegister
from composting.views.submissions import Submissions
from composting.tests.test_base import IntegrationTestBase, FunctionalTestBase

from pyramid.httpexceptions import HTTPBadRequest


EDIT_URL = "http://test.enketo.org/edit?id=1"


@urlmatch(netloc=r'(.*\.)?test.ona\.io$')
def fetch_non_existent_submission_url(url, request):
    return {
        'status_code': 404,
        'content': '{"code": 404, "detail": "Not Found"}'
    }


@urlmatch(netloc='test.ona.io', path='/api/v1/data/wb_composting/')
def enketo_edit_url_mock(url, request):
    return {
        'status_code': 201,
        'content': '{"url": "http://test.enketo.org/edit?id=1"}'
    }


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

    def test_edit_submission_with_invalid_submission(self):
        daily_waste = DailyWaste.newest()
        self.request.context = daily_waste

        with HTTMock(fetch_non_existent_submission_url):
            self.assertRaises(HTTPBadRequest, self.views.edit)

    def test_edit_submission_with_valid_submission(self):
        daily_waste = DailyWaste.newest()
        self.request.context = daily_waste

        with HTTMock(enketo_edit_url_mock):
            response = self.views.edit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, EDIT_URL)


class TestSubmissionsFunctional(FunctionalTestBase):

    def setUp(self):
        super(TestSubmissionsFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_submission_list_when_admin_user(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'daily-waste'),
            _query={Submission.PENDING: '1', Submission.REJECTED: '1'})
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        # also tests daily-waste response status
        self.assertEqual(response.status_code, 200)

    def test_submission_list_when_current_site_user(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'daily-waste'),
            _query={Submission.PENDING: '1', Submission.REJECTED: '1'})
        headers = self._login_user(2)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_submission_list_when_other_site_user(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'daily-waste'),
            _query={Submission.PENDING: '1', Submission.REJECTED: '1'})
        headers = self._login_user(3)
        self.testapp.get(url, headers=headers, status=403)

    def test_daily_waste_show(self):
        monthly_density = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(monthly_density.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_monthly_waste_composition_show(self):
        monthly_waste = MonthlyWasteComposition.newest()
        url = self.request.route_path(
            'submissions', traverse=(monthly_waste.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_windrow_monitoring_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'windrow-monitoring'),
            _query={Submission.PENDING: '1', Submission.REJECTED: '1'})
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_windrow_monitoring_show(self):
        monthly_waste = WindrowMonitoring.newest()
        url = self.request.route_path(
            'submissions', traverse=(monthly_waste.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_daily_rejects_landfilled_show(self):
        daily_reject = DailyRejectsLandfilled.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_reject.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_density_of_rejects_from_sieving_show(self):
        rejects_density = MonthlyRejectsDensity.newest()
        url = self.request.route_path(
            'submissions', traverse=(rejects_density.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_municipality_electricity_register_show(self):
        electricity_register = ElectricityRegister.newest()
        url = self.request.route_path(
            'submissions', traverse=(electricity_register.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_leachete_monthly_register_show(self):
        electricity_register = LeacheteMonthlyRegister.newest()
        url = self.request.route_path(
            'submissions', traverse=(electricity_register.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_compost_sales_register_show(self):
        compost_sale = CompostSalesRegister.newest()
        url = self.request.route_path(
            'submissions', traverse=(compost_sale.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_compost_density_register_show(self):
        compost_density = CompostDensityRegister.newest()
        url = self.request.route_path(
            'submissions', traverse=(compost_density.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_monthly_rejects_composition_show(self):
        rejects_composition = MonthlyRejectsComposition.newest()
        url = self.request.route_path(
            'submissions', traverse=(rejects_composition.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_daily_vehicle_data_register_show(self):
        rejects_composition = DailyVehicleDataRegister.newest()
        url = self.request.route_path(
            'submissions', traverse=(rejects_composition.id,))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_approve_post_fail_if_missing_csrf_token(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_waste.id, 'approve'))
        headers = self._login_user(1)
        self.testapp.post(url, headers=headers, status=400)

    def test_reject_post_fail_if_missing_csrf_token(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_waste.id, 'reject'))
        headers = self._login_user(1)
        self.testapp.post(url, headers=headers, status=400)

    def test_unapprove_post_fail_if_missing_csrf_token(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'submissions', traverse=(daily_waste.id, 'unapprove'))
        headers = self._login_user(1)
        self.testapp.post(url, headers=headers, status=400)

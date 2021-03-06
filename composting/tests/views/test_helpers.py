import unittest

from datetime import date
from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, Response
from pyramid import testing

from composting.models import Submission, DailyWaste
from composting.models.municipality import Municipality
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.site_report import SiteReport
from composting.views import helpers
from composting.tests.test_base import IntegrationTestBase


class TestHelpers(unittest.TestCase):
    def test_selections_from_request(self):
        request = testing.DummyRequest()
        request.GET = MultiDict([
            ('pending', '1'),
            ('approved', '1')
        ])
        selection_list = ['pending', 'approved', 'rejected']
        selections = helpers.selections_from_request(
            request, selection_list, lambda v: v == '1', 'pending')
        self.assertEqual(sorted(selections), ['approved', 'pending'])

    def test_selections_from_request_returns_defaults_if_no_matches(self):
        request = testing.DummyRequest()
        request.GET = MultiDict([
            ('not-pending', '1'),
            ('not-approved', '1')
        ])
        selection_list = ['pending', 'approved', 'rejected']
        selections = helpers.selections_from_request(
            request, selection_list, lambda v: v == '1', ['pending'])
        self.assertEqual(sorted(selections), ['pending'])

    def test_get_trend_data(self):
        site_report_1 = SiteReport(
            report_date=date.today(),
            report_json={'volume_of_mature_compost': 10,
                         'electricity_consumption': 150})
        site_report_2 = SiteReport(
            report_date=date.today(),
            report_json={'volume_of_mature_compost': 10,
                         'electricity_consumption': 200})

        site_reports = [site_report_1, site_report_2]
        trend_data_map = helpers.get_trend_data(site_reports)
        self.assertIsInstance(trend_data_map, dict)
        self.assertIsNotNone(trend_data_map['volume_of_mature_compost'])
        self.assertIsNotNone(trend_data_map['electricity_consumption'])


class TestHelpersIntegration(IntegrationTestBase):
    def setUp(self):
        super(TestHelpersIntegration, self).setUp()
        self.setup_test_data()
        municipality_id = Municipality.get(Municipality.name == "Mukono").id
        self.context = DailyWaste(
            xform_id=DailyWaste.XFORM_ID,
            status=Submission.PENDING,
            # add dummy json data for volume calculation
            date=date(2014, 6, 13),
            json_data={
                'compressor_truck': 'yes',
                'volume': '20'
            },
            municipality_submission=MunicipalitySubmission(
                municipality_id=municipality_id
            ))
        self.request = testing.DummyRequest()

    def test_update_status(self):
        self.request.wrapped_response = Response()
        self.request.new_status = Submission.APPROVED
        response = helpers.update_status(self.context, self.request)
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(
            response.location,
            self.request.route_url(
                'municipalities',
                traverse=('1', self.context.__class__.LIST_ACTION_NAME)))
        self.assertEqual(self.context.status, Submission.APPROVED)

    def test_update_status_raises_value_error_if_no_new_status(self):
        self.request.wrapped_response = Response()
        self.request.action = 'some-action'
        self.assertRaises(
            ValueError, helpers.update_status, self.context, self.request)

    def test_update_status_raises_value_error_if_no_action(self):
        self.request.wrapped_response = Response()
        self.request.new_status = Submission.APPROVED

        class BadSubmissionType(Submission):
            # missing a LIST_ACTION_NAME property
            pass

        self.assertRaises(
            ValueError, helpers.update_status, BadSubmissionType(),
            self.request)

    def test_is_current_path_returns_true_if_path_info_matches(self):
        self.request.environ['PATH_INFO'] = '/municipalities/1/daily-waste'
        path = self.request.route_path(
            'municipalities', traverse=(1, 'daily-waste'))
        result = helpers.is_current_path(self.request, path)
        self.assertTrue(result)

    def test_is_current_path_returns_false_if_path_info_not_match(self):
        self.request.environ['PATH_INFO'] = '/municipalities/1/monthly-density'
        path = self.request.route_path(
            'municipalities', traverse=(1, 'daily-waste'))
        result = helpers.is_current_path(self.request, path)
        self.assertFalse(result)

    def test_update_status_returns_the_wrapped_status_as_is_if_not_200(self):
        wrapped_response = HTTPBadRequest("Very bad request")
        self.request.wrapped_response = wrapped_response
        response = helpers.update_status(self.context, self.request)
        self.assertEqual(response, wrapped_response)

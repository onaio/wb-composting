import unittest

from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPFound
from pyramid import testing

from composting import constants
from composting.models import Submission, DailyWaste
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


class TestHelpersIntegration(IntegrationTestBase):
    def setUp(self):
        super(TestHelpersIntegration, self).setUp()
        self.context = DailyWaste(
            xform_id=constants.DAILY_WASTE_REGISTER_FORM,
            status=Submission.PENDING)
        self.request = testing.DummyRequest()

    def test_update_status(self):
        self.request.new_status = Submission.APPROVED
        self.request.action = 'some-action'
        response = helpers.update_status(self.context, self.request)
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(
            response.location,
            self.request.route_url(
                'municipalities', traverse=('1', self.request.action)))
        self.assertEqual(self.context.status, Submission.APPROVED)

    def test_update_status_raises_value_error_if_no_new_status(self):
        self.request.action = 'some-action'
        self.assertRaises(
            ValueError, helpers.update_status, self.context, self.request)

    def test_update_status_raises_value_error_if_no_action(self):
        self.request.new_status = Submission.APPROVED
        self.assertRaises(
            ValueError, helpers.update_status, self.context, self.request)
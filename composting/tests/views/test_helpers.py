import unittest

from webob.multidict import MultiDict
from pyramid import testing

from composting.views.helpers import selections_from_request


class TestHelpers(unittest.TestCase):
    def test_selections_from_request(self):
        request = testing.DummyRequest()
        request.GET = MultiDict([
            ('pending', '1'),
            ('approved', '1')
        ])
        selection_list = ['pending', 'approved', 'rejected']
        selections = selections_from_request(
            request, selection_list, lambda v: v == '1', 'pending')
        self.assertEqual(sorted(selections), ['approved', 'pending'])

    def test_selections_from_request_returns_defaults_if_no_matches(self):
        request = testing.DummyRequest()
        request.GET = MultiDict([
            ('not-pending', '1'),
            ('not-approved', '1')
        ])
        selection_list = ['pending', 'approved', 'rejected']
        selections = selections_from_request(
            request, selection_list, lambda v: v == '1', ['pending'])
        self.assertEqual(sorted(selections), ['pending'])
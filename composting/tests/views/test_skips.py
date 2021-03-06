from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPFound
from pyramid import testing

from composting.tests.test_base import (
    IntegrationTestBase, FunctionalTestBase)

from composting.models import Municipality, Skip
from composting.views.skips import Skips


class TestSkips(IntegrationTestBase):
    def setUp(self):
        super(TestSkips, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()
        self.views = Skips(self.request)
        self.municipality = Municipality.get(Municipality.name == "Mukono")
        self.skip = Skip.get(
            Skip.municipality == self.municipality, Skip.skip_type == "A")

    def test_edit_skip_post(self):
        skip_id = self.skip.id
        self.request.context = self.skip
        self.request.method = 'POST'
        self.request.POST = MultiDict([
            ('skip_type', 'A'),
            ('small_length', '25.5'),
            ('large_length', '30.0'),
            ('small_breadth', '16.0'),
            ('large_breadth', '20.0')
        ])
        result = self.views.edit()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(
            result.location,
            self.request.route_url('skips', traverse=(skip_id, 'edit')))
        skip = Skip.get(Skip.id == skip_id)
        self.assertEqual(skip.small_length, 25.5)


class TestSkipsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestSkipsFunctional, self).setUp()
        self.setup_test_data()

    def test_edit_skip_get(self):
        skip = Skip.newest()
        url = self.request.route_path('skips', traverse=(skip.id, 'edit'))
        headers = self._login_user(2)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_edit_skip_post_fails_if_missing_csrf_token(self):
        skip = Skip.newest()
        url = self.request.route_path('skips', traverse=(skip.id, 'edit'))
        headers = self._login_user(1)
        self.testapp.post(url, MultiDict([
            ('skip_type', 'Z'),
            ('small_length', '20'),
            ('large_length', '30'),
            ('small_breadth', '16'),
            ('large_breadth', '20')
        ]), headers=headers, status=400)

    def test_delete_skip_post_fails_if_missing_csrf_token(self):
        skip = Skip.newest()
        url = self.request.route_path('skips', traverse=(skip.id, 'delete'))
        headers = self._login_user(1)
        self.testapp.post(url, headers=headers, status=400)
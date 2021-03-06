from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPFound
from pyramid import testing

from composting.views.auth import sign_in, sign_out
from composting.tests.test_base import IntegrationTestBase, FunctionalTestBase


class TestAuthViews(IntegrationTestBase):
    def test_sign_in_post(self):
        self.setup_test_data()
        request = testing.DummyRequest(post=MultiDict([
            ('username', 'admin'),
            ('password', 'admin')
        ]))
        result = sign_in(request)
        self.assertIsInstance(result, HTTPFound)

    def test_sign_out(self):
        response = sign_out(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url('municipalities', traverse=()))


class TestAuthViewsFunctional(FunctionalTestBase):
    def test_sign_in_get(self):
        url = self.request.route_path('auth', action='sign-in')
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
from pyramid import testing

from composting.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)
from composting.views.default import default


class TestDefault(IntegrationTestBase):
    def test_home_view_response(self):
        request = testing.DummyRequest()
        response = default(request)
        self.assertEqual(response, {})


class TestDefaultFunctional(FunctionalTestBase):
    def test_home_view_response(self):
        url = self.request.route_url('default')
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

from pyramid import testing

from wbcomposting.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)
from wbcomposting.views.default import home


class TestHomeView(IntegrationTestBase):
    def test_home_view_response(self):
        request = testing.DummyRequest()
        response = home(request)
        self.assertEqual(response, {})


class TestHomeViewFunctional(FunctionalTestBase):
    def test_home_view_response(self):
        url = self.request.route_url('default')
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

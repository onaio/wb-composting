from pyramid import testing

from composting.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)
from composting.views.default import default


class TestDefaultFunctional(FunctionalTestBase):
    def test_home_view_response(self):
        url = self.request.route_url('default')
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url('municipalities', traverse=()))

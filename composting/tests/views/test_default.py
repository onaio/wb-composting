from pyramid import testing

from composting.tests.test_base import (
    IntegrationTestBase,
    FunctionalTestBase)
from composting.views.default import default


class TestDefaultFunctional(FunctionalTestBase):
    def test_home_view_response(self):
        self.setup_test_data()
        url = self.request.route_url('default')
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            self.request.route_url('municipalities', traverse=()))
        response.follow(headers=headers)

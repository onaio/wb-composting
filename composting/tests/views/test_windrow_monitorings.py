from composting.models.municipality import Municipality
from composting.tests.test_base import IntegrationTestBase, FunctionalTestBase


class TestWindrowMonitorings(IntegrationTestBase):
    pass


class TestWindrowMonitoringsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestWindrowMonitoringsFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_show_for_admin_user(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'windrows', '@@', 'W5-5/12/2014',))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_show_for_current_site_user(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'windrows', '@@', 'W5-5/12/2014',))
        headers = self._login_user(2)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_show_for_other_site_user(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'windrows', '@@', 'W5-5/12/2014',))
        headers = self._login_user(3)
        self.testapp.get(url, headers=headers, status=403)
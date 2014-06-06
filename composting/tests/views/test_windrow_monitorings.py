from composting.models.municipality import Municipality
from composting.tests.test_base import IntegrationTestBase, FunctionalTestBase


class TestWindrowMonitorings(IntegrationTestBase):
    pass


class TestWindrowMonitoringsFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestWindrowMonitoringsFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_show(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'windrows', '@@', 'W5-5/12/2014',))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
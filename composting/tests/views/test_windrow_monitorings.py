from composting.models.municipality import Municipality
from composting.models.submission import Submission
from composting.models.report import Report
from composting.tests.test_base import IntegrationTestBase, FunctionalTestBase
from composting.models.windrow_monitoring import WindrowMonitoring


class TestWindrowMonitorings(IntegrationTestBase):

    def test_create_or_update_report(self):
        self.setup_test_data()
        report_count = Report.count()
        windrow_monitor = WindrowMonitoring.all()[0]

        windrow_monitor.status = Submission.APPROVED

        self.assertEqual(Report.count(), report_count + 1)


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

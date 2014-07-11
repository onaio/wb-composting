from composting.libs.windrow_monitoring_handler import WindrowMonitoringHandler
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.windrow_monitoring import WindrowMonitoring
from composting.tests.test_base import TestBase


class TestWindrowMonitoringHandler(TestBase):
    klass = WindrowMonitoring
    xform_id = WindrowMonitoring.XFORM_ID
    date_string = '2014-04-21'

    def test_can_handle(self):
        json_payload = {
            '_xform_id_string': self.xform_id
        }
        result = WindrowMonitoringHandler.can_handle(json_payload)
        self.assertTrue(result)

    def test_create_submission(self):
        json_payload = {
            '_xform_id_string': self.xform_id,
            'date': self.date_string,
            'windrow_number': 'W5-21/5/2014',
            'week_no': '1'
        }
        submission = WindrowMonitoringHandler.create_submission(
            json_payload)
        self.assertIsInstance(submission, WindrowMonitoring)

    def test__call__(self):
        self.setup_test_data()
        json_payload = {
            '_submitted_by': 'manager',
            '_xform_id_string': self.xform_id,
            'date': self.date_string,
            'windrow_number': 'W5-21/5/2014',
            'week_no': '1',
            '_id': '12345'
        }
        handler = WindrowMonitoringHandler()
        num_submissions = self.klass.count()
        num_municipality_submissions = MunicipalitySubmission.count()
        handler.__call__(json_payload)
        self.assertEqual(self.klass.count(), num_submissions + 1)
        self.assertEqual(
            MunicipalitySubmission.count(), num_municipality_submissions + 1)

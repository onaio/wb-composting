import pytz
import transaction

from datetime import datetime
from pyramid import testing
from mock import MagicMock
from sqlalchemy.orm.attributes import instance_state

from composting.models.base import DBSession
from composting.models.submission import Submission, SubmissionFactory
from composting.models.report import Report
from composting.tests.test_base import TestBase


class TestSubmission(TestBase):
    def setUp(self):
        super(TestSubmission, self).setUp()
        self.setup_test_data()

    def test_get_item(self):
        submission = DBSession.query(Submission).first()
        submission_id = submission.id
        item = SubmissionFactory(testing.DummyRequest())[submission.id]
        self.assertIsInstance(item, Submission)
        self.assertEqual(submission_id, item.id)

    def test_get_item_raises_key_error_if_not_found(self):
        factory = SubmissionFactory(testing.DummyRequest())
        self.assertRaises(KeyError, factory.__getitem__, 0)

    def test_locale_submission_time(self):
        datetime_string = '2014-05-22T14:14:18'
        submission = Submission(json_data={
            '_submission_time': datetime_string
        })
        submission_time = datetime.strptime(
            datetime_string, '%Y-%m-%dT%H:%M:%S')
        submission_time = pytz.utc.localize(submission_time).astimezone(
            pytz.timezone('Africa/Kampala'))
        locale_datetime = submission.locale_submission_time()
        self.assertEqual(locale_datetime, submission_time)

    def test_get_or_create_report_returns_new_report_if_none_exists(self):
        submission = Submission.newest()
        report = submission.get_or_create_report()
        self.assertFalse(instance_state(report).persistent)

    def test_get_or_create_report_returns_existing_report_if_one_exist(self):
        submission = Submission.newest()
        submission_id = submission.id
        report = Report(submission=submission, report_json={'key': 'value'})
        with transaction.manager:
            DBSession.add(report)
        submission = Submission.get(Submission.id == submission_id)
        report = submission.get_or_create_report()
        self.assertTrue(instance_state(report).persistent)

    def test_delete_report(self):
        submission = Submission.newest()
        submission_id = submission.id
        report = Report(
            submission=submission, report_json={'key': 'value'})
        with transaction.manager:
            DBSession.add(report)
        num_reports = Report.count(Report.submission_id == submission_id)
        self.assertEqual(num_reports, 1)

        submission = Submission.get(Submission.id == submission_id)
        submission.delete_report()
        self.assertEqual(
            Report.count(Report.submission_id == submission_id),
            num_reports - 1)

    def test_set_approved_calls_create_or_update_report(self):
        submission = Submission(status=Submission.PENDING)
        submission.create_or_update_report = MagicMock(
            name='create_or_update_report')
        submission.status = Submission.APPROVED
        submission.create_or_update_report.assert_called_with()

    def test_set_pending_calls_delete_report(self):
        submission = Submission(status=Submission.APPROVED)
        submission.delete_report = MagicMock(name='delete_report')
        submission.status = Submission.PENDING
        submission.delete_report.assert_called_with()

    def test_set_rejected_calls_delete_report(self):
        submission = Submission(status=Submission.PENDING)
        submission.delete_report = MagicMock(name='delete_report')
        submission.status = Submission.REJECTED
        submission.delete_report.assert_called_with()

    def test_can_approve_returns_true_if_pending(self):
        # can_approve should be True if
        submission = Submission(status=Submission.PENDING)
        self.assertTrue(submission.can_approve(testing.DummyRequest()))

    def test_can_approve_returns_false_if_not_pending(self):
        # can_approve should be True if
        submission = Submission(status=Submission.APPROVED)
        self.assertFalse(submission.can_approve(testing.DummyRequest()))
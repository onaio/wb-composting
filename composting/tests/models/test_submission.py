from pyramid import testing

from composting.models.base import DBSession
from composting.models.submission import Submission, SubmissionFactory
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
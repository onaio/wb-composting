from composting.models.submission import Submission
from composting.tests.test_base import TestBase


class TestSubmission(TestBase):
    def setUp(self):
        super(TestSubmission, self).setUp()
        self.setup_test_data()

    def test_get_items_without_criterion(self):
        submissions = Submission.get_items()
        self.assertEqual(len(submissions), len(self.submissions))

    def test_get_items_with_criterion(self):
        pending_submissions = filter(
            lambda s: s[0] == Submission.PENDING, self.submissions)
        criterion = Submission.status == Submission.PENDING
        submissions = Submission.get_items(criterion)
        self.assertEqual(len(submissions), len(pending_submissions))
from composting.models.submission import Submission
from composting.tests.test_base import TestBase


class TestSubmission(TestBase):
    def setUp(self):
        super(TestSubmission, self).setUp()
        self.setup_test_data()
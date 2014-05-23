from dashboard.constants import XFORM_ID_STRING

from composting import constants
from composting.libs.municipality_submission_handler import (
    MunicipalitySubmissionHandler)
from composting.models.monthly_density import MonthlyDensity
from composting.models.daily_waste import DailyWaste
from composting.models.municipality_submission import MunicipalitySubmission
from composting.tests.test_base import TestBase


class TestMunicipalitySubmissionHandler(TestBase):
    def test_can_handle_monthly_density_submission(self):
        json_payload = {
            XFORM_ID_STRING: constants.MONTHLY_WASTE_DENSITY_FORM
        }
        result = MunicipalitySubmissionHandler.can_handle(json_payload)
        self.assertTrue(result)

    def test_creates_monthly_waste_submission(self):
        json_payload = {
            XFORM_ID_STRING: constants.MONTHLY_WASTE_DENSITY_FORM,
            MonthlyDensity.DATE_FIELD: '2014-04-21T10:34:03.000'
        }
        submission = MunicipalitySubmissionHandler.create_submission(
            json_payload)
        self.assertIsInstance(submission, MonthlyDensity)

    def test_call_on_monthly_density(self):
        self.setup_test_data()
        json_payload = {
            XFORM_ID_STRING: constants.MONTHLY_WASTE_DENSITY_FORM,
            MonthlyDensity.DATE_FIELD: '2014-04-21T10:34:03.000'
        }
        handler = MunicipalitySubmissionHandler()
        num_submissions = MonthlyDensity.count()
        num_municipality_submissions = MunicipalitySubmission.count()
        handler.__call__(json_payload)
        self.assertEqual(MonthlyDensity.count(), num_submissions + 1)
        self.assertEqual(
            MunicipalitySubmission.count(), num_municipality_submissions + 1)

    def test_can_handle_daily_waste_submission(self):
        json_payload = {
            XFORM_ID_STRING: constants.DAILY_WASTE_REGISTER_FORM
        }
        result = MunicipalitySubmissionHandler.can_handle(json_payload)
        self.assertTrue(result)

    def test_creates_daily_waste_submission(self):
        json_payload = {
            XFORM_ID_STRING: constants.DAILY_WASTE_REGISTER_FORM,
            DailyWaste.DATE_FIELD: '2014-04-21T10:34:03.000'
        }
        submission = MunicipalitySubmissionHandler.create_submission(
            json_payload)
        self.assertIsInstance(submission, DailyWaste)

    def test_call_on_daily_waste_submission(self):
        self.setup_test_data()
        json_payload = {
            XFORM_ID_STRING: constants.DAILY_WASTE_REGISTER_FORM,
            DailyWaste.DATE_FIELD: '2014-04-21T10:34:03.000'
        }
        handler = MunicipalitySubmissionHandler()
        num_submissions = DailyWaste.count()
        num_municipality_submissions = MunicipalitySubmission.count()
        handler.__call__(json_payload)
        self.assertEqual(DailyWaste.count(), num_submissions + 1)
        self.assertEqual(
            MunicipalitySubmission.count(), num_municipality_submissions + 1)
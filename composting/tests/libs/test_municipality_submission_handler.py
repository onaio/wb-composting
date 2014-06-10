from dashboard.constants import XFORM_ID_STRING

from composting import constants
from composting.libs.municipality_submission_handler import (
    MunicipalitySubmissionHandler)
from composting.models.monthly_density import MonthlyDensity
from composting.models.daily_waste import DailyWaste
from composting.models.monthly_waste_composition import MonthlyWasteComposition
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.daily_rejects_landfilled import DailyRejectsLandfilled
from composting.models.monthly_rejects_density import MonthlyRejectsDensity
from composting.models.electricity_register import ElectricityRegister
from composting.tests.test_base import TestBase


class TestDailyWasteSubmissionHandling(TestBase):
    klass = DailyWaste
    xform_id = constants.DAILY_WASTE_REGISTER_FORM
    date_string = '2014-04-21T10:34:03.000'

    def test_can_handle(self):
        json_payload = {
            XFORM_ID_STRING: self.xform_id
        }
        result = MunicipalitySubmissionHandler.can_handle(json_payload)
        self.assertTrue(result)

    def test_create_submission(self):
        json_payload = {
            XFORM_ID_STRING: self.xform_id,
            self.klass.DATE_FIELD: self.date_string
        }
        submission = MunicipalitySubmissionHandler.create_submission(
            json_payload)
        self.assertIsInstance(submission, self.klass)

    def test__call__(self):
        self.setup_test_data()
        json_payload = {
            XFORM_ID_STRING: self.xform_id,
            self.klass.DATE_FIELD: self.date_string
        }
        handler = MunicipalitySubmissionHandler()
        num_submissions = self.klass.count()
        num_municipality_submissions = MunicipalitySubmission.count()
        handler.__call__(json_payload)
        self.assertEqual(self.klass.count(), num_submissions + 1)
        self.assertEqual(
            MunicipalitySubmission.count(), num_municipality_submissions + 1)


class TestMonthlyDensitySubmissionHandling(TestDailyWasteSubmissionHandling):
    klass = MonthlyDensity
    xform_id = constants.MONTHLY_WASTE_DENSITY_FORM


class TestMonthlyWasteCompositionSubmissionHandling(
        TestDailyWasteSubmissionHandling):
    klass = MonthlyWasteComposition
    xform_id = constants.MONTHLY_WASTE_COMPOSITION_FORM
    date_string = '2014-04-21'


class TestDailyRejectsLandfilledSubmissionHandling(
        TestDailyWasteSubmissionHandling):
    klass = DailyRejectsLandfilled
    xform_id = DailyRejectsLandfilled.XFORM_ID
    date_string = '2014-04-21'


class TestMonthlyRejectsDensitySubmissionHandling(
        TestDailyWasteSubmissionHandling):
    klass = MonthlyRejectsDensity
    xform_id = MonthlyRejectsDensity.XFORM_ID
    date_string = '2014-04-21'


class TestElectricityRegisterSubmissionHandling(
        TestDailyWasteSubmissionHandling):
    klass = ElectricityRegister
    xform_id = ElectricityRegister.XFORM_ID
    date_string = '2014-04-21'
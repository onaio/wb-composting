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
from composting.models.leachete_monthly_register import LeacheteMonthlyRegister
from composting.models.compost_sales_register import CompostSalesRegister
from composting.models.compost_density_register import CompostDensityRegister
from composting.models.submission import Submission
from composting.models.monthly_rejects_composition import (
    MonthlyRejectsComposition)
from composting.models.daily_vehicle_register import DailyVehicleDataRegister
from composting.tests.test_base import TestBase


class TestMunicipalitySubmissionHandler(TestBase):
    def setUp(self):
        super(TestMunicipalitySubmissionHandler, self).setUp()
        self.setup_test_data()

    def test_get_municipality_from_payload_returns_none_if_key_is_none(self):
        municipality = MunicipalitySubmissionHandler\
            .get_municipality_from_payload({})
        self.assertIsNone(municipality)

    def test_get_municipality_from_payload(self):
        json_payload = {
            constants.SUBMITTED_BY: 'jinja_manager'
        }
        municipality = MunicipalitySubmissionHandler\
            .get_municipality_from_payload(json_payload)
        self.assertEqual(municipality.name, "Jinja")

    def test_get_municipality_from_payload_returns_none_if_not_found(self):
        json_payload = {
            constants.SUBMITTED_BY: 'admin'
        }
        municipality = MunicipalitySubmissionHandler\
            .get_municipality_from_payload(json_payload)
        self.assertIsNone(municipality)

    def test_submission_updating(self):
        submission = Submission.get(
            Submission.json_data[constants.ONA_SUBMISSION_ID].astext ==
            str(52559))
        json_payload = {
            constants.SUBMITTED_BY: 'manager',
            XFORM_ID_STRING: DailyWaste.XFORM_ID,
            DailyWaste.DATE_FIELD: '2014-04-21T10:34:03.000',
            constants.ONA_SUBMISSION_ID: '52559'
        }
        handler = MunicipalitySubmissionHandler()
        num_municipality_submissions = MunicipalitySubmission.count()
        handler.__call__(json_payload)

        self.assertEqual(MunicipalitySubmission.count(),
                         num_municipality_submissions)

        submission = Submission.get(
            Submission.json_data[constants.ONA_SUBMISSION_ID].astext ==
            str(52559))
        self.assertEqual(submission.json_data, json_payload)


class TestDailyWasteSubmissionHandling(TestBase):
    klass = DailyWaste
    xform_id = DailyWaste.XFORM_ID
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
            constants.SUBMITTED_BY: 'manager',
            XFORM_ID_STRING: self.xform_id,
            self.klass.DATE_FIELD: self.date_string,
            constants.ONA_SUBMISSION_ID: '23456'
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
    xform_id = MonthlyDensity.XFORM_ID


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


class TestLeacheteMonthlyRegisterSubmissionHandling(
        TestDailyWasteSubmissionHandling):
    klass = LeacheteMonthlyRegister
    xform_id = LeacheteMonthlyRegister.XFORM_ID
    date_string = '2014-04-21'


class TestCompostSalesRegisterSubmissionHandling(
        TestDailyWasteSubmissionHandling):
    klass = CompostSalesRegister
    xform_id = CompostSalesRegister.XFORM_ID
    date_string = '2014-04-21'


class TestCompostDensityRegisterSubmissionHandling(
        TestDailyWasteSubmissionHandling):
    klass = CompostDensityRegister
    xform_id = CompostDensityRegister.XFORM_ID
    date_string = '2014-04-21'


class TestMonthlyRejectsCompositionSubmissionHandling(
        TestDailyWasteSubmissionHandling):
    klass = MonthlyRejectsComposition
    xform_id = MonthlyRejectsComposition.XFORM_ID
    date_string = '2014-04-21'


class TestDailyVehicleSubmissionHandling(
        TestDailyWasteSubmissionHandling):
    klass = DailyVehicleDataRegister
    xform_id = DailyVehicleDataRegister.XFORM_ID
    date_string = '2014-04-21'

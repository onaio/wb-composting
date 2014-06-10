from dashboard.constants import XFORM_ID_STRING
from dashboard.libs import SubmissionHandler

from composting import constants
from composting.models.base import DBSession
from composting.models.municipality import Municipality
from composting.models.monthly_density import MonthlyDensity
from composting.models.monthly_waste_composition import MonthlyWasteComposition
from composting.models.daily_waste import DailyWaste
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.windrow_monitoring import WindrowMonitoring
from composting.models.daily_rejects_landfilled import DailyRejectsLandfilled
from composting.models.monthly_rejects_density import MonthlyRejectsDensity
from composting.models.electricity_register import ElectricityRegister
from composting.models.leachete_monthly_register import LeacheteMonthlyRegister


class MunicipalitySubmissionHandler(SubmissionHandler):
    # mapping of id strings to classes
    XFORM_CLASS_MAPPING = {
        constants.MONTHLY_WASTE_DENSITY_FORM: MonthlyDensity,
        constants.DAILY_WASTE_REGISTER_FORM: DailyWaste,
        constants.MONTHLY_WASTE_COMPOSITION_FORM: MonthlyWasteComposition,
        WindrowMonitoring.XFORM_ID: WindrowMonitoring,
        DailyRejectsLandfilled.XFORM_ID: DailyRejectsLandfilled,
        MonthlyRejectsDensity.XFORM_ID: MonthlyRejectsDensity,
        ElectricityRegister.XFORM_ID: ElectricityRegister,
        LeacheteMonthlyRegister.XFORM_ID: LeacheteMonthlyRegister
    }

    @staticmethod
    def can_handle(json_payload):
        return json_payload[XFORM_ID_STRING] in [
            constants.MONTHLY_WASTE_DENSITY_FORM,
            constants.DAILY_WASTE_REGISTER_FORM,
            constants.MONTHLY_WASTE_COMPOSITION_FORM,
            DailyRejectsLandfilled.XFORM_ID,
            MonthlyRejectsDensity.XFORM_ID,
            ElectricityRegister.XFORM_ID,
            LeacheteMonthlyRegister.XFORM_ID
        ]

    @staticmethod
    def create_submission(json_payload, **kwargs):
        xform_id = json_payload[XFORM_ID_STRING]
        # get the specific submission sub-class
        try:
            klass = MunicipalitySubmissionHandler.XFORM_CLASS_MAPPING[xform_id]
        except KeyError:
            raise ValueError("No xform class mapping to '{}'".format(xform_id))
        else:
            # determine the date the data is in reference of
            date = klass.datetime_from_json(
                json_payload, klass.DATE_FIELD, klass.DATE_FORMAT).date()
            return klass(
                xform_id=json_payload[XFORM_ID_STRING],
                json_data=json_payload,
                date=date,
                **kwargs)

    def __call__(self, json_payload, **kwargs):
        submission = self.create_submission(json_payload, **kwargs)
        # add the submission because we can save even when we can't determine
        # its municipality
        DBSession.add(submission)

        # todo: determine the municipality id
        municipality_id = 1
        municipality = Municipality.get(Municipality.id == municipality_id)

        municipality_submission = MunicipalitySubmission(
            submission=submission,
            municipality=municipality)

        # todo: save just the submission when if we don't have a municipality
        DBSession.add(municipality_submission)
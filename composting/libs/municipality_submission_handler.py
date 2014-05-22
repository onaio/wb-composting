from dashboard.constants import XFORM_ID_STRING
from dashboard.libs import SubmissionHandler

from composting import constants
from composting.models.base import DBSession
from composting.models.municipality import Municipality
from composting.models.monthly_density import MonthlyDensity
from composting.models.municipality_submission import MunicipalitySubmission


class MunicipalitySubmissionHandler(SubmissionHandler):
    # mapping of id strings to classes
    XFORM_CLASS_MAPPING = {
        constants.MONTHLY_WASTE_DENSITY_FORM: MonthlyDensity
    }

    @staticmethod
    def can_handle(json_payload):
        return json_payload[XFORM_ID_STRING] in [
            constants.MONTHLY_WASTE_DENSITY_FORM
        ]

    @staticmethod
    def create_submission(json_payload):
        # get the specific submission sub-class
        klass = MunicipalitySubmissionHandler.XFORM_CLASS_MAPPING[
            json_payload[XFORM_ID_STRING]]

        # determine the date the data is in reference of
        date = klass.date_from_json(json_payload)
        return klass(
            xform_id=json_payload[XFORM_ID_STRING],
            json_data=json_payload,
            date=date)

    def __call__(self, json_payload, **kwargs):
        submission = self.create_submission(json_payload)
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
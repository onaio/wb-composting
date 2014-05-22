from dashboard.constants import XFORM_ID_STRING
from dashboard.libs import SubmissionHandler

from composting import constants
from composting.models.base import DBSession
from composting.models.municipality import Municipality
from composting.models.monthly_density import MonthlyDensity
from composting.models.municipality_submission import MunicipalitySubmission


class MonthlyDensityHandler(SubmissionHandler):
    @staticmethod
    def can_handle(json_payload):
        return json_payload[XFORM_ID_STRING] in [
            constants.MONTHLY_WASTE_DENSITY_FORM
        ]

    def __call__(self, json_payload, **kwargs):
        submission = MonthlyDensity(
            xform_id=json_payload[XFORM_ID_STRING], json_data=json_payload)

        # todo: determine the municipality id
        municipality_id = 1
        municipality = Municipality.get(Municipality.id == municipality_id)

        # determine the date the data is in reference of
        date = submission.date

        municipality_submission = MunicipalitySubmission(
            submission=submission,
            date=date,
            municipality=municipality)

        # todo: save just the submission when if we don't have a municipality
        DBSession.add(municipality_submission)
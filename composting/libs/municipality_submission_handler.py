from dashboard.constants import XFORM_ID_STRING
from dashboard.libs import SubmissionHandler

from composting import constants
from composting.models.submission import Submission
from composting.models.municipality_submission import MunicipalitySubmission


class MunicipalitySubmissionHandler(SubmissionHandler):
    @staticmethod
    def can_handle(json_payload):
        return json_payload[XFORM_ID_STRING] in [
            constants.MONTHLY_WASTE_DENSITY_FORM
        ]

    def __call__(self, json_payload, **kwargs):
        submission = Submission(
            xform_id=json_payload[XFORM_ID_STRING], json_data=json_payload)
        # todo: determine the municipality id
        municipality_id = 1
        # determine the date the data is in reference of
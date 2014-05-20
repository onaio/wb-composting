from dashboard.constants import XFORM_ID_STRING
from dashboard.libs import SubmissionHandler

from composting import constants
from composting.models.submission import Submission
from composting.models.daily_waste import DailyWaste


class DailyWasteSubmissionHandler(SubmissionHandler):
    @staticmethod
    def can_handle(json_payload):
        return (json_payload[XFORM_ID_STRING] ==
                constants.DAILY_WASTE_REGISTER_FORM)

    def __call__(self, json_payload):
        xform_id = json_payload[XFORM_ID_STRING]
        # create a submission
        submission = Submission(
            xform_id=xform_id, json_data=json_payload)
        daily_waste = DailyWaste(submission=submission)
        daily_waste.save()
        return daily_waste
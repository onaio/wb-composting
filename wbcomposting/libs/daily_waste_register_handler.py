from dashboard.constants import XFORM_ID_STRING
from dashboard.libs import SubmissionHandler

from wbcomposting import constants


class DailyWasteSubmissionHandler(SubmissionHandler):
    @staticmethod
    def can_handle(json_payload):
        return (json_payload[XFORM_ID_STRING] ==
                constants.DAILY_WASTE_REGISTER_FORM)
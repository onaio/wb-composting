from dashboard.constants import XFORM_ID_STRING

from composting.models.windrow_monitoring import WindrowMonitoring
from municipality_submission_handler import MunicipalitySubmissionHandler


class WindrowMonitoringHandler(MunicipalitySubmissionHandler):
    @staticmethod
    def can_handle(json_payload):
        return json_payload[XFORM_ID_STRING] == WindrowMonitoring.XFORM_ID

    @staticmethod
    def create_submission(json_payload, **kwargs):
        submission = MunicipalitySubmissionHandler.create_submission(
            json_payload,
            windrow_no=json_payload[WindrowMonitoring.WINDROW_NO_FIELD],
            week_no=json_payload[WindrowMonitoring.WEEK_NO_FIELD],
            **kwargs)
        return submission
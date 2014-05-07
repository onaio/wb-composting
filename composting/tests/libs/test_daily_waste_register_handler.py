import json

from dashboard.constants import XFORM_ID_STRING
from composting.tests.test_base import TestBase
from composting.libs import DailyWasteSubmissionHandler
from composting.models import Submission, DailyWaste


class TestDailyWasteRegisterHandler(TestBase):
    def test_can_handle_returns_true_for_matching_id_string(self):
        json_payload = {"_xform_id_string": "daily_waste_register"}
        self.assertTrue(DailyWasteSubmissionHandler.can_handle(json_payload))

    def test_can_handle_returns_false_for_mismatching_id_string(self):
        json_payload = {"_xform_id_string": "not_daily_waste_register"}
        self.assertFalse(DailyWasteSubmissionHandler.can_handle(json_payload))

    def test_call_persists_waste_register_payload(self):
        handler = DailyWasteSubmissionHandler()
        json_payload = json.loads('{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27735c", "municipal_council": "Hahbs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "Kaj 123k", "skip_number": "10B", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "no", "_status": "submitted_via_web", "today": "2014-04-28", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "A", "clerk_signature": "1398686267686.jpg", "date": "2014-04-28T14:56:00.000+03", "waste_height": "250.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-28T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52559}')  # noqa
        num_submissions = Submission.count()
        num_daily_wastes = DailyWaste.count()
        handler.__call__(json_payload)
        self.assertEqual(Submission.count(), num_submissions + 1)
        self.assertEqual(DailyWaste.count(), num_daily_wastes + 1)

        # get newest submission and daily waste records
        submission = Submission.newest()
        daily_waste = DailyWaste.newest()
        self.assertEqual(submission.xform_id, json_payload[XFORM_ID_STRING])
        self.assertEqual(submission.json_data, json_payload)
        self.assertEqual(daily_waste.submission, submission)
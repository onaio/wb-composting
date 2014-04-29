import unittest

from wbcomposting.libs import DailyWasteSubmissionHandler


class TestDailyWasteRegisterHandler(unittest.TestCase):
    def test_can_handle_returns_true_for_matching_id_string(self):
        json_payload = {"_xform_id_string": "daily_waste_register"}
        self.assertTrue(DailyWasteSubmissionHandler.can_handle(json_payload))

    def test_can_handle_returns_false_for_mismatching_id_string(self):
        json_payload = {"_xform_id_string": "not_daily_waste_register"}
        self.assertFalse(DailyWasteSubmissionHandler.can_handle(json_payload))
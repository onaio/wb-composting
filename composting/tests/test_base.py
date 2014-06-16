import os
import unittest
import transaction
import json

from pyramid.registry import Registry
from pyramid import testing
from pyramid.paster import (
    get_appsettings
)
from pyramid.security import IAuthenticationPolicy
from sqlalchemy import engine_from_config
from webtest import TestApp

from dashboard.libs.submission_handler import (
    submission_handler_manager)

from composting import main, hook_submission_handlers
from composting.security import pwd_context
from composting.libs.municipality_submission_handler import (
    MunicipalitySubmissionHandler)
from composting.models.base import (
    DBSession,
    Base)
from composting.models import Municipality, Submission, Skip
from composting.models.user import User


SETTINGS_FILE = 'test.ini'
settings = get_appsettings(SETTINGS_FILE)
engine = engine_from_config(settings, 'sqlalchemy.')


class TestBase(unittest.TestCase):
    submissions = [
        # Daily Waste
        (Submission.PENDING, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27735c", "municipal_council": "Hahbs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "Kaj 123k", "skip_number": "10B", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "no", "_status": "submitted_via_web", "today": "2014-04-28", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "A", "clerk_signature": "1398686267686.jpg", "datetime": "2014-04-28T14:56:00.000+03", "waste_height": "250.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-28T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52559}'),
        (Submission.APPROVED, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27736c", "municipal_council": "Jahjs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "1234", "skip_number": "11", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "no", "_status": "submitted_via_web", "today": "2014-04-29", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "B", "clerk_signature": "1398686267686.jpg", "datetime": "2014-04-29T14:56:00.000+03", "waste_height": "13.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-29T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52560}'),
        # submission without a valid skip type
        (Submission.APPROVED, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27736c", "municipal_council": "Jahjs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "1234", "skip_number": "11", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "yes", "_status": "submitted_via_web", "today": "2014-04-29", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "F", "clerk_signature": "1398686267686.jpg", "datetime": "2014-04-29T14:56:00.000+03", "volume": "30.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-29T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52561}'),
        # Monthly Density
        (Submission.PENDING, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "datetime": "2014-01-03T15:35:00.000+03", "_xform_id_string": "monthly_waste_density_register", "_geolocation": ["-1.29430537", "36.78711405"], "meta/instanceID": "uuid:b47bd251-560f-4e73-8569-8ef095d52873", "end": "2014-05-21T15:36:30.893+03", "skip_number": "5", "start": "2014-05-21T15:35:29.611+03", "location": "-1.29430537 36.78711405 1781.0 14.0", "compressor_truck": "no", "_status": "submitted_via_web", "filled_weight": "1.2", "_uuid": "b47bd251-560f-4e73-8569-8ef095d52873", "skip_type": "A", "clerk_signature": "1400675787603.jpg", "waste_height": "8.0", "formhub/uuid": "f7b67d7d1fbf4e5f89dcf9c479af6a43", "_submission_time": "2014-05-21T12:36:52", "empty_weight": "0.8", "_attachments": ["wb_composting/attachments/1400675787603.jpg"], "_id": 60116}'),
        (Submission.APPROVED, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "datetime": "2014-01-03T16:15:00.000+03", "_xform_id_string": "monthly_waste_density_register", "_geolocation": ["-1.29430537", "36.78711405"], "meta/instanceID": "uuid:b47bd251-560f-4e73-8569-8ef095d52873", "end": "2014-05-21T15:36:30.893+03", "skip_number": "5", "start": "2014-05-21T15:35:29.611+03", "location": "-1.29430537 36.78711405 1781.0 14.0", "compressor_truck": "no", "_status": "submitted_via_web", "filled_weight": "1.2", "_uuid": "b47bd251-560f-4e73-8569-8ef095d52873", "skip_type": "A", "clerk_signature": "1400675787603.jpg", "waste_height": "8.0", "formhub/uuid": "f7b67d7d1fbf4e5f89dcf9c479af6a43", "_submission_time": "2014-05-21T12:36:52", "empty_weight": "0.8", "_attachments": ["wb_composting/attachments/1400675787603.jpg"], "_id": 60117}'),
        (Submission.APPROVED, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "datetime": "2014-01-14T06:15:00.000+03", "_xform_id_string": "monthly_waste_density_register", "_geolocation": ["-1.29430537", "36.78711405"], "meta/instanceID": "uuid:b47bd251-560f-4e73-8569-8ef095d52873", "end": "2014-05-21T15:36:30.893+03", "skip_number": "5", "start": "2014-05-21T15:35:29.611+03", "location": "-1.29430537 36.78711405 1781.0 14.0", "compressor_truck": "yes", "_status": "submitted_via_web", "filled_weight": "1.4", "_uuid": "b47bd251-560f-4e73-8569-8ef095d52873", "volume": "2000.0", "clerk_signature": "1400675787603.jpg", "waste_height": "9.0", "formhub/uuid": "f7b67d7d1fbf4e5f89dcf9c479af6a43", "_submission_time": "2014-05-21T12:36:52", "empty_weight": "0.8", "_attachments": ["wb_composting/attachments/1400675787603.jpg"], "_id": 60120}'),
        (Submission.PENDING, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "datetime": "2014-05-21T15:35:00.000+03", "_xform_id_string": "monthly_waste_density_register", "_geolocation": ["-1.29430537", "36.78711405"], "meta/instanceID": "uuid:b47bd251-560f-4e73-8569-8ef095d52873", "end": "2014-05-21T15:36:30.893+03", "skip_number": "5", "start": "2014-05-21T15:35:29.611+03", "location": "-1.29430537 36.78711405 1781.0 14.0", "compressor_truck": "no", "_status": "submitted_via_web", "filled_weight": "1.2", "_uuid": "b47bd251-560f-4e73-8569-8ef095d52873", "skip_type": "A", "clerk_signature": "1400675787603.jpg", "waste_height": "8.0", "formhub/uuid": "f7b67d7d1fbf4e5f89dcf9c479af6a43", "_submission_time": "2014-05-21T12:36:52", "empty_weight": "0.8", "_attachments": ["wb_composting/attachments/1400675787603.jpg"], "_id": 60118}'),
        (Submission.REJECTED, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "datetime": "2014-05-11T15:35:00.000+03", "_xform_id_string": "monthly_waste_density_register", "_geolocation": ["-1.29430537", "36.78711405"], "meta/instanceID": "uuid:b47bd251-560f-4e73-8569-8ef095d52873", "end": "2014-05-21T15:36:30.893+03", "skip_number": "5", "start": "2014-05-21T15:35:29.611+03", "location": "-1.29430537 36.78711405 1781.0 14.0", "compressor_truck": "no", "_status": "submitted_via_web", "filled_weight": "1.2", "_uuid": "b47bd251-560f-4e73-8569-8ef095d52873", "skip_type": "A", "clerk_signature": "1400675787603.jpg", "waste_height": "8.0", "formhub/uuid": "f7b67d7d1fbf4e5f89dcf9c479af6a43", "_submission_time": "2014-05-21T12:36:52", "empty_weight": "0.8", "_attachments": ["wb_composting/attachments/1400675787603.jpg"], "_id": 60119}'),
        # Monthly waste composition
        (Submission.PENDING, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "monthly_waste_composition", "_geolocation": ["-1.29430433", "36.7870352"], "textiles": "0.8", "meta/instanceID": "uuid:15eb3284-4c57-4f8c-badb-60ce771ea850", "end": "2014-06-03T11:33:41.013+03", "start": "2014-06-03T11:32:40.846+03", "skip_number": "2", "food_waste": "2.8", "location": "-1.29430433 36.7870352 1750.0 19.0", "_status": "submitted_via_web", "paper_pulp": "1.3", "clerk_signature": "1401784418384.jpg", "_uuid": "15eb3284-4c57-4f8c-badb-60ce771ea850", "glass_plastics_metal": "0.6", "formhub/uuid": "21c6e2256be44993b7dff8c234ab8692", "_id": 63977, "garden_yard_waste": "0.0", "_submission_time": "2014-06-03T08:34:09", "_attachments": ["wb_composting/attachments/1401784418384.jpg"], "month_year": "2014-05-01", "wood_products": "2.9"}'),
        # Windrow monitoring
        (Submission.PENDING, '{"_notes": [], "windrow_turned": "no", "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "windrow_monitoring_form", "meta/instanceID": "uuid:0caa13fd-eec1-45ac-85d5-0eaf200c7db0", "windrow_number": "W5-5/12/2014", "end": "2014-06-06T10:31:55.462+03", "start": "2014-06-06T10:28:43.158+03", "location": "-1.29445178 36.78708937 1754.0 11.0", "_attachments": ["wb_composting/attachments/1402039913458.jpg"], "_status": "submitted_via_web", "formhub/uuid": "5fee918d54d74844b1b4f672eec85665", "monitoring_group/o4": "36", "moisture_added": "yes", "monitoring_group/o5": "39", "_uuid": "0caa13fd-eec1-45ac-85d5-0eaf200c7db0", "monitoring_group/o3": "21", "monitoring_group/o2": "30", "monitoring_group/o1": "35", "date": "2014-06-06", "monitoring_group/t4": "13", "monitoring_group/t5": "18", "monitoring_group/t2": "14", "monitoring_group/t3": "25", "monitoring_group/t1": "12", "_submission_time": "2014-06-06T07:32:25", "clerk_signature": "1402039913458.jpg", "week_no": "1", "_geolocation": ["-1.29445178", "36.78708937"], "_id": 64647}'),
        # Daily rejects land-filled
        (Submission.PENDING, '{"barrows_number_frm_sieving": "8", "_notes": [], "_uuid": "c7605549-0aba-4421-8919-be04b5e03f91", "end": "2014-06-09T11:21:25.700+03", "_submission_time": "2014-06-09T08:21:55", "_id": 65506, "clerk_signature": "1402302083802.jpg", "_bamboo_dataset_id": "", "_tags": [], "_attachments": ["wb_composting/attachments/1402302083802.jpg"], "start": "2014-06-09T11:20:59.158+03", "barrows_number_frm_sorting": "12", "location": "-1.29435036 36.78726554 1785.0 14.0", "meta/instanceID": "uuid:c7605549-0aba-4421-8919-be04b5e03f91", "_xform_id_string": "register_daily_rejects_landfilled", "date": "2014-06-09", "_status": "submitted_via_web", "_geolocation": ["-1.29435036", "36.78726554"], "formhub/uuid": "74394d71864a442c8a405037f70acb60"}'),
        # Monthly Density of Rejects from Sieving
        (Submission.PENDING, '{"filled_box_weight": "48.0", "_notes": [], "_uuid": "73386661-a2a4-48a7-b064-7aeb01b746b2", "end": "2014-06-09T12:42:30.991+03", "_submission_time": "2014-06-09T09:42:59", "_id": 65524, "clerk_signature": "1402306949221.jpg", "_bamboo_dataset_id": "", "_tags": [], "_attachments": ["wb_composting/attachments/1402306949221.jpg"], "start": "2014-06-09T12:41:59.599+03", "location": "-1.29429363 36.78710502 1789.0 13.0", "meta/instanceID": "uuid:73386661-a2a4-48a7-b064-7aeb01b746b2", "_xform_id_string": "monthly_density_rejects_from_sieving", "empty_box_weight": "12.0", "_status": "submitted_via_web", "_geolocation": ["-1.29429363", "36.78710502"], "month_year": "2014-06-01", "formhub/uuid": "a46662760eb041aa95d6d813b6034e58"}'),
        # Electricity Register
        (Submission.PENDING, '{"_notes": [], "_uuid": "7bd9e297-1ebe-4acb-bdfe-e3453223b728", "end": "2014-06-10T11:19:23.770+03", "bill_amount": "9850.35", "_submission_time": "2014-06-10T08:19:54", "bill_reading": "857.0", "clerk_signature": "1402388361464.jpg", "_bamboo_dataset_id": "", "_tags": [], "_attachments": ["wb_composting/attachments/1402388361464.jpg"], "start": "2014-06-10T11:18:29.911+03", "_id": 65653, "location": "-1.29451103 36.78725329 1762.0 14.0", "meta/instanceID": "uuid:7bd9e297-1ebe-4acb-bdfe-e3453223b728", "_xform_id_string": "municipality_electricity_register", "month_year": "2014-04-01", "_status": "submitted_via_web", "_geolocation": ["-1.29451103", "36.78725329"], "meter_reading": "857.0", "formhub/uuid": "98498729ffc244bbb4012b07bf7845ec"}'),
        (Submission.PENDING, '{"_notes": [], "_uuid": "7bd9e297-1ebe-4acb-bdfe-e3453223b728", "end": "2014-06-10T11:19:23.770+03", "bill_amount": "12000.0", "_submission_time": "2014-06-10T08:19:54", "bill_reading": "1205.0", "clerk_signature": "1402388361464.jpg", "_bamboo_dataset_id": "", "_tags": [], "_attachments": ["wb_composting/attachments/1402388361464.jpg"], "start": "2014-06-10T11:18:29.911+03", "_id": 65653, "location": "-1.29451103 36.78725329 1762.0 14.0", "meta/instanceID": "uuid:7bd9e297-1ebe-4acb-bdfe-e3453223b728", "_xform_id_string": "municipality_electricity_register", "month_year": "2014-05-01", "_status": "submitted_via_web", "_geolocation": ["-1.29451103", "36.78725329"], "meter_reading": "1208.0", "formhub/uuid": "98498729ffc244bbb4012b07bf7845ec"}'),
        # Leachete monthly
        (Submission.PENDING, '{"_notes": [], "_uuid": "1b862f50-a4c1-4757-aa54-409535092406", "end": "2014-06-10T14:45:30.474+03", "formhub/uuid": "3ce340718fb2426c9243f52308674118", "_bamboo_dataset_id": "", "_submission_time": "2014-06-10T11:46:02", "_id": 65683, "after_pumping/dateTime_after_pumping": "2014-05-06T14:22:00.000+03", "before_pumping/fbHeight_be4_pumping": "12.86", "_tags": [], "clerk_signature": "1402400725828.jpg", "_attachments": ["wb_composting/attachments/1402400725828.jpg"], "start": "2014-06-10T14:44:09.106+03", "_geolocation": ["-1.29443756", "36.78711353"], "after_pumping/fbHeight_after_pumping": "5.7", "_xform_id_string": "leachate_monthly_register", "month_year": "2014-05-01", "_status": "submitted_via_web", "meta/instanceID": "uuid:1b862f50-a4c1-4757-aa54-409535092406", "before_pumping/dateTime_be4_pumping": "2014-05-05T10:44:00.000+03", "location": "-1.29443756 36.78711353 1783.0 15.0"}'),
        # Monthly compost density
        (Submission.PENDING, '{"filled_box_weight": "2.8", "_notes": [], "_uuid": "968bf79e-fde6-45ce-8c56-28aa99544f45", "end": "2014-06-11T11:53:16.121+03", "_submission_time": "2014-06-11T08:53:47", "_id": 67210, "clerk_signature": "1402476794233.jpg", "_bamboo_dataset_id": "", "_tags": [], "_attachments": ["wb_composting/attachments/1402476794233.jpg"], "start": "2014-06-11T11:52:33.951+03", "location": "-1.29439702 36.78710472 1733.0 30.0", "meta/instanceID": "uuid:968bf79e-fde6-45ce-8c56-28aa99544f45", "_xform_id_string": "monthly_compost_density_register", "empty_box_weight": "1.0", "_status": "submitted_via_web", "_geolocation": ["-1.29439702", "36.78710472"], "month_year": "2014-05-01", "formhub/uuid": "23e6551242454a9fb7599432067b79b8"}'),
        # Compost sales
        (Submission.PENDING, '{"_notes": [], "bagged_compost_weight": "1.2", "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "compost_sales_register", "_geolocation": ["-1.29440324", "36.78710531"], "meta/instanceID": "uuid:4ae93b5b-4779-4ce0-8ad7-532d887bfc47", "end": "2014-06-11T10:25:51.023+03", "vehicle_number": "UQG128K", "start": "2014-06-11T10:24:57.524+03", "location": "-1.29440324 36.78710531 1743.0 48.0", "_status": "submitted_via_web", "supply_location": "Mukono", "clerk_signature": "1402471548292.jpg", "_uuid": "4ae93b5b-4779-4ce0-8ad7-532d887bfc47", "date": "2014-06-11", "invoice_number": "123456", "supply_distance": "1.5", "bagged_compost": "yes", "formhub/uuid": "6f5b918f534a455d9fa78853f8f61b5c", "_submission_time": "2014-06-11T07:28:54", "_attachments": ["wb_composting/attachments/1402471548292.jpg"], "_id": 67196}'),
        (Submission.PENDING, '{"_notes": [], "compost_height": "1.5", "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "compost_sales_register", "meta/instanceID": "uuid:3baf4c3f-7eb9-43f1-a0a7-abc5ee1c480f", "end": "2014-06-11T10:28:21.988+03", "vehicle_number": "UAG527F", "start": "2014-06-11T10:25:53.396+03", "location": "-1.29443009 36.78726494 1773.0 26.0", "_attachments": ["wb_composting/attachments/1402471699300.jpg"], "compost_width": "2.0", "_status": "submitted_via_web", "supply_location": "Jinja", "clerk_signature": "1402471699300.jpg", "_uuid": "3baf4c3f-7eb9-43f1-a0a7-abc5ee1c480f", "date": "2014-06-12", "invoice_number": "54683", "supply_distance": "25.0", "bagged_compost": "no", "formhub/uuid": "6f5b918f534a455d9fa78853f8f61b5c", "_submission_time": "2014-06-11T07:28:55", "_geolocation": ["-1.29443009", "36.78726494"], "compost_length": "4.3", "_id": 67197}'),
        # Composition from sieving
        (Submission.PENDING, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "monthly_composition_rejects_from_sieving", "meta/instanceID": "uuid:1be41841-a019-45c9-b01c-82da8ae8f2d6", "textiles": "4.5", "total_mature_compost": "60.0", "end": "2014-06-11T15:47:01.123+03", "food_waste": "0.0", "start": "2014-06-11T15:46:03.980+03", "location": "-1.29470097 36.78711762 1756.0 32.0", "_attachments": ["wb_composting/attachments/1402490818542.jpg"], "_status": "submitted_via_web", "paper_pulp": "0.5", "clerk_signature": "1402490818542.jpg", "_uuid": "1be41841-a019-45c9-b01c-82da8ae8f2d6", "glass_plastics_metal": "18.0", "garden_yard_waste": "0.0", "formhub/uuid": "1e5ccc56e1b44984841f3cbdd8ed7801", "_id": 67307, "sieved_compost": "16.0", "_submission_time": "2014-06-11T12:47:36", "_geolocation": ["-1.29470097", "36.78711762"], "month_year": "2014-05-01", "wood_products": "21.0"}'),
        # Daily vehicle data
        (Submission.PENDING, '{"bill_photo": "1402560339447.jpg", "eod_odometer_reading": "125627.0", "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_vehicle_data_register", "fuel_purchased_liters": "12.3", "meta/instanceID": "uuid:61306375-2cd4-44bc-ab54-c4d8d93dff27", "end": "2014-06-12T11:06:08.344+03", "vehicle_number": "UAG263L", "operation_hours": "3.5", "start": "2014-06-12T11:04:40.864+03", "_geolocation": ["-1.29432612", "36.78719833"], "location": "-1.29432612 36.78719833 1747.0 30.0", "_status": "submitted_via_web", "bill_reference": "B12345", "clerk_signature": "1402560365863.jpg", "sod_odometer_reading": "125080.0", "_uuid": "61306375-2cd4-44bc-ab54-c4d8d93dff27", "date": "2014-05-14", "formhub/uuid": "2b5699ccdf494644bb4e8802fd7766ee", "fuel_purchased": "yes", "_submission_time": "2014-06-12T08:06:41", "_notes": [], "_attachments": ["wb_composting/attachments/1402560365863.jpg", "wb_composting/attachments/1402560339447.jpg"], "_id": 67707}')
    ]

    def setUp(self):
        registry = Registry()
        registry.settings = settings
        self.config = testing.setUp(registry=registry)
        pwd_context.load_path('test.ini')
        # setup db
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        Base.metadata.drop_all()
        Base.metadata.create_all()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def setup_test_data(self):
        admin = User(username='admin', password='admin')
        manager = User(username='manager', password='manager')
        municipality = Municipality(name="Mukono")
        skip_a = Skip(
            municipality=municipality, skip_type='A', small_length=20,
            large_length=30, small_breadth=10, large_breadth=16)
        submission_handler_manager.clear()
        hook_submission_handlers()
        with transaction.manager:
            DBSession.add_all([admin, manager, municipality, skip_a])
            for status, raw_json in self.submissions:
                json_payload = json.loads(raw_json)
                handler_class = submission_handler_manager.find_handler(
                    json_payload)
                handler_class().__call__(json_payload, status=status)

    def get_submissions_by_xform_id(self, xform_id):
        return filter(
            lambda s: json.loads(s[1])['_xform_id_string'] == xform_id,
            self.submissions)


class IntegrationTestBase(TestBase):
    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        self.config.include('composting')
        self.request = testing.DummyRequest()


class FunctionalTestBase(IntegrationTestBase):
    def _login_user(self, userid):
        policy = self.testapp.app.registry.queryUtility(IAuthenticationPolicy)
        headers = policy.remember(self.request, userid)
        cookie_parts = dict(headers)['Set-Cookie'].split('; ')
        cookie = filter(
            lambda i: i.split('=')[0] == 'auth_tkt', cookie_parts)[0]
        return {'Cookie': cookie}

    def setUp(self):
        super(FunctionalTestBase, self).setUp()
        current_dir = os.getcwd()
        app = main(
            {
                '__file__': os.path.join(current_dir, SETTINGS_FILE),
                'here': current_dir
            },
            **settings)
        self.testapp = TestApp(app, extra_environ={
            'HTTP_HOST': 'example.com'
        })

        # used by cookie auth as the domain
        self.request.environ = {
            'SERVER_NAME': 'example.com',
        }


class TestInclude(IntegrationTestBase):
    def test_submission_handlers_included(self):
        self.assertIn(
            MunicipalitySubmissionHandler, submission_handler_manager)
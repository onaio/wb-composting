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
from composting import constants
from composting.libs.municipality_submission_handler import (
    MunicipalitySubmissionHandler)
from composting.models.base import (
    DBSession,
    Base)
from composting.models import Municipality, Submission, Skip


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
        (Submission.PENDING, '{"_notes": [], "windrow_turned": "no", "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "windrow_monitoring_form", "meta/instanceID": "uuid:0caa13fd-eec1-45ac-85d5-0eaf200c7db0", "windrow_number": "W5-5/12/2014", "end": "2014-06-06T10:31:55.462+03", "start": "2014-06-06T10:28:43.158+03", "location": "-1.29445178 36.78708937 1754.0 11.0", "_attachments": ["wb_composting/attachments/1402039913458.jpg"], "_status": "submitted_via_web", "formhub/uuid": "5fee918d54d74844b1b4f672eec85665", "monitoring_group/o4": "36", "moisture_added": "yes", "monitoring_group/o5": "39", "_uuid": "0caa13fd-eec1-45ac-85d5-0eaf200c7db0", "monitoring_group/o3": "21", "monitoring_group/o2": "30", "monitoring_group/o1": "35", "date": "2014-06-06", "monitoring_group/t4": "13", "monitoring_group/t5": "18", "monitoring_group/t2": "14", "monitoring_group/t3": "25", "monitoring_group/t1": "12", "_submission_time": "2014-06-06T07:32:25", "clerk_signature": "1402039913458.jpg", "week_no": "1", "_geolocation": ["-1.29445178", "36.78708937"], "_id": 64647}')
    ]

    def setUp(self):
        registry = Registry()
        registry.settings = settings
        self.config = testing.setUp(registry=registry)
        # setup db
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        Base.metadata.drop_all()
        Base.metadata.create_all()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def setup_test_data(self):
        municipality = Municipality(name="Mukono")
        skip_a = Skip(
            municipality=municipality, skip_type='A', small_length=20,
            large_length=30, small_breadth=10, large_breadth=16)
        submission_handler_manager.clear()
        hook_submission_handlers()
        with transaction.manager:
            DBSession.add_all([municipality, skip_a])
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
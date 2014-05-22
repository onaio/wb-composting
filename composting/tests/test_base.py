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
    submission_handler_manager, NoAppropriateHandlerException)

from composting import main, hook_submission_handlers
from composting.libs import DailyWasteSubmissionHandler
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
        (Submission.PENDING, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27735c", "municipal_council": "Hahbs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "Kaj 123k", "skip_number": "10B", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "no", "_status": "submitted_via_web", "today": "2014-04-28", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "A", "clerk_signature": "1398686267686.jpg", "date": "2014-04-28T14:56:00.000+03", "waste_height": "250.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-28T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52559}'),
        (Submission.APPROVED, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27736c", "municipal_council": "Jahjs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "1234", "skip_number": "11", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "no", "_status": "submitted_via_web", "today": "2014-04-29", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "B", "clerk_signature": "1398686267686.jpg", "date": "2014-04-29T14:56:00.000+03", "waste_height": "13.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-29T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52559}'),
        (Submission.APPROVED, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27736c", "municipal_council": "Jahjs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "1234", "skip_number": "11", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "yes", "_status": "submitted_via_web", "today": "2014-04-29", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "F", "clerk_signature": "1398686267686.jpg", "date": "2014-04-29T14:56:00.000+03", "volume": "30.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-29T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52559}'),
        # Monthly Density
        (Submission.PENDING, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "datetime": "2014-01-03T15:35:00.000+03", "_xform_id_string": "monthly_waste_density_register", "_geolocation": ["-1.29430537", "36.78711405"], "meta/instanceID": "uuid:b47bd251-560f-4e73-8569-8ef095d52873", "end": "2014-05-21T15:36:30.893+03", "skip_number": "5", "start": "2014-05-21T15:35:29.611+03", "location": "-1.29430537 36.78711405 1781.0 14.0", "compressor_truck": "no", "_status": "submitted_via_web", "filled_weight": "1.2", "_uuid": "b47bd251-560f-4e73-8569-8ef095d52873", "skip_type": "A", "clerk_signature": "1400675787603.jpg", "waste_height": "8.0", "formhub/uuid": "f7b67d7d1fbf4e5f89dcf9c479af6a43", "_submission_time": "2014-05-21T12:36:52", "empty_weight": "0.8", "_attachments": ["wb_composting/attachments/1400675787603.jpg"], "_id": 60116}'),
        (Submission.PENDING, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "datetime": "2014-05-21T15:35:00.000+03", "_xform_id_string": "monthly_waste_density_register", "_geolocation": ["-1.29430537", "36.78711405"], "meta/instanceID": "uuid:b47bd251-560f-4e73-8569-8ef095d52873", "end": "2014-05-21T15:36:30.893+03", "skip_number": "5", "start": "2014-05-21T15:35:29.611+03", "location": "-1.29430537 36.78711405 1781.0 14.0", "compressor_truck": "no", "_status": "submitted_via_web", "filled_weight": "1.2", "_uuid": "b47bd251-560f-4e73-8569-8ef095d52873", "skip_type": "A", "clerk_signature": "1400675787603.jpg", "waste_height": "8.0", "formhub/uuid": "f7b67d7d1fbf4e5f89dcf9c479af6a43", "_submission_time": "2014-05-21T12:36:52", "empty_weight": "0.8", "_attachments": ["wb_composting/attachments/1400675787603.jpg"], "_id": 60116}')
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


class IntegrationTestBase(TestBase):
    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        self.config.include('composting')


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
        self.testapp = TestApp(app)
        self.request = testing.DummyRequest()
        self.request.environ = {
            'SERVER_NAME': 'example.com',
        }


class TestInclude(IntegrationTestBase):
    def test_submission_handlers_included(self):
        self.assertIn(DailyWasteSubmissionHandler, submission_handler_manager)
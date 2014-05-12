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

from dashboard.libs.submission_handler import submission_handler_manager

from composting import main
from composting.libs import DailyWasteSubmissionHandler
from composting.models.base import (
    DBSession,
    Base)
from composting.models import Municipality, Submission


SETTINGS_FILE = 'test.ini'
settings = get_appsettings(SETTINGS_FILE)
engine = engine_from_config(settings, 'sqlalchemy.')


class TestBase(unittest.TestCase):
    daily_waste_submissions = [
        (Submission.PENDING, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27735c", "municipal_council": "Hahbs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "Kaj 123k", "skip_number": "10B", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "no", "_status": "submitted_via_web", "today": "2014-04-28", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "A", "clerk_signature": "1398686267686.jpg", "date": "2014-04-28T14:56:00.000+03", "waste_height": "250.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-28T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52559}'),
        (Submission.APPROVED, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27736c", "municipal_council": "Jahjs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "1234", "skip_number": "11", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "no", "_status": "submitted_via_web", "today": "2014-04-29", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "B", "clerk_signature": "1398686267686.jpg", "date": "2014-04-29T14:56:00.000+03", "waste_height": "13.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-29T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52559}'),
        (Submission.APPROVED, '{"_notes": [], "_bamboo_dataset_id": "", "_tags": [], "_xform_id_string": "daily_waste_register", "meta/instanceID": "uuid:d0998c99-9147-476b-b393-56254c27736c", "municipal_council": "Jahjs", "end": "2014-04-28T14:57:51.208+03", "vehicle_number": "1234", "skip_number": "11", "start": "2014-04-28T14:56:36.215+03", "location": "-1.29435992 36.78708972 1792.0 15.0", "compressor_truck": "yes", "_status": "submitted_via_web", "today": "2014-04-29", "_uuid": "d0998c99-9147-476b-b393-56254c27735c", "skip_type": "F", "clerk_signature": "1398686267686.jpg", "date": "2014-04-29T14:56:00.000+03", "volume": "30.0", "formhub/uuid": "16b00ce47f224ebc8ca010aa606464f0", "_attachments": ["wb_composting/attachments/1398686267686.jpg"], "_submission_time": "2014-04-29T11:58:13", "_geolocation": ["-1.29435992", "36.78708972"], "deviceid": "358239056515325", "_id": 52559}')
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
        with transaction.manager:
            for status, submission in self.daily_waste_submissions:
                daily_waste = DailyWasteSubmissionHandler().__call__(
                    json.loads(submission))
                daily_waste.submission.status = status
            DBSession.add_all([municipality])


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
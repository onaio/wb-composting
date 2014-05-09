from pyramid.httpexceptions import HTTPFound
from pyramid import testing
from pyramid.response import Response

from composting.models.base import DBSession
from composting.models import DailyWaste, Submission
from composting.views.daily_wastes import DailyWastes
from composting.tests.test_base import IntegrationTestBase, FunctionalTestBase


class TestDailyWastes(IntegrationTestBase):
    def setUp(self):
        super(TestDailyWastes, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()
        self.views = DailyWastes(self.request)

    @classmethod
    def get_daily_waste_record(cls, *criterion):
        return DBSession.query(DailyWaste)\
            .join(DailyWaste.submission)\
            .filter(*criterion)[0]

    def test_show(self):
        result = self.views.show()
        self.assertEqual(result.keys(), [])

    def test_approve(self):
        result = self.views.approve()
        self.assertIsInstance(result, Response)
        self.assertEqual(self.request.new_status, Submission.APPROVED)
        self.assertEqual(self.request.action, 'daily-waste')

    def test_reject(self):
        result = self.views.reject()
        self.assertIsInstance(result, Response)
        self.assertEqual(self.request.new_status, Submission.REJECTED)
        self.assertEqual(self.request.action, 'daily-waste')

    def test_unapprove(self):
        result = self.views.unapprove()
        self.assertIsInstance(result, Response)
        self.assertEqual(self.request.new_status, Submission.PENDING)
        self.assertEqual(self.request.action, 'daily-waste')


class TestDailyWastesFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestDailyWastesFunctional, self).setUp()
        self.setup_test_data()

    def test_show(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'daily-waste', traverse=(daily_waste.id,))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_approve(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'daily-waste', traverse=(daily_waste.id, 'approve'))
        result = self.testapp.post(url)
        self.assertEqual(result.status_code, 302)

    def test_reject(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'daily-waste', traverse=(daily_waste.id, 'reject'))
        result = self.testapp.post(url)
        self.assertEqual(result.status_code, 302)

    def test_unapprove(self):
        daily_waste = DailyWaste.newest()
        url = self.request.route_path(
            'daily-waste', traverse=(daily_waste.id, 'unapprove'))
        result = self.testapp.post(url)
        self.assertEqual(result.status_code, 302)
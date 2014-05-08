from pyramid.httpexceptions import HTTPFound
from pyramid import testing

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
        self.request.method = 'POST'
        daily_waste = self.get_daily_waste_record(
            Submission.status == Submission.PENDING)
        daily_waste_id = daily_waste.id
        self.request.context = daily_waste
        result = self.views.approve()
        self.assertIsInstance(result, HTTPFound)

        # check that it was approved
        daily_waste = DailyWaste.get(DailyWaste.id == daily_waste_id)
        self.assertEqual(daily_waste.submission.status, Submission.APPROVED)

    def test_reject(self):
        self.request.method = 'POST'
        daily_waste = self.get_daily_waste_record(
            Submission.status == Submission.APPROVED)
        daily_waste_id = daily_waste.id
        self.request.context = daily_waste
        result = self.views.reject()
        self.assertIsInstance(result, HTTPFound)

        # check that it was rejected
        daily_waste = DailyWaste.get(DailyWaste.id == daily_waste_id)
        self.assertEqual(daily_waste.submission.status, Submission.REJECTED)

    def test_unapprove(self):
        self.request.method = 'POST'
        daily_waste = self.get_daily_waste_record(
            Submission.status == Submission.APPROVED)
        daily_waste_id = daily_waste.id
        self.request.context = daily_waste
        result = self.views.unapprove()
        self.assertIsInstance(result, HTTPFound)

        # check that it was set to pending
        daily_waste = DailyWaste.get(DailyWaste.id == daily_waste_id)
        self.assertEqual(daily_waste.submission.status, Submission.PENDING)


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
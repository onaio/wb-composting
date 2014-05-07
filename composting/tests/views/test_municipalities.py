from pyramid import testing
from webob.multidict import MultiDict

from composting.tests.test_base import (
    IntegrationTestBase, FunctionalTestBase)

from composting.models import Municipality
from composting.views.municipalities import Municipalities, Submission


class TestMunicipalities(IntegrationTestBase):
    def setUp(self):
        super(TestMunicipalities, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()
        self.view = Municipalities(self.request)

    def test_index(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        self.request.context = municipality
        result = self.view.index()
        self.assertEqual(result['municipality'], municipality)

    def test_daily_waste_list(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        self.request.context = municipality
        self.request.GET = MultiDict([
            ('pending', '1'),
            ('rejected', '1')
        ])
        result = self.view.daily_waste_list()
        self.assertEqual(result['municipality'], municipality)
        self.assertEqual(len(result['daily_wastes']), 1)


class TestMunicipalitiesFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestMunicipalitiesFunctional, self).setUp()
        self.setup_test_data()

    def test_index(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        url = self.request.route_path(
            'municipalities', traverse=(municipality.id,))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_daily_waste_list(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        url = self.request.route_path(
            'municipalities',
            traverse=(municipality.id, 'daily-waste'),
            _query={Submission.PENDING: '1', Submission.REJECTED: '1'})
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def _test_daily_waste_show(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        daily_waste_record = None
        url = self.request.route_path(
            'municipalities', traverse=(municipality.id, 'daily-waste'))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)
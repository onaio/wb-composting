from pyramid import testing

from composting.tests.test_base import (
    IntegrationTestBase, FunctionalTestBase)

from composting.models import Municipality
from composting.views.municipalities import Municipalities


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

    def test_daily_waste(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        self.request.context = municipality
        result = self.view.daily_waste()
        self.assertEqual(result['municipality'], municipality)


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

    def test_daily_waste(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        url = self.request.route_path(
            'municipalities', traverse=(municipality.id, 'daily-waste'))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)
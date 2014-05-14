from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPFound
from pyramid import testing

from composting.tests.test_base import (
    IntegrationTestBase, FunctionalTestBase)

from composting.models import Municipality, Skip
from composting.views.municipalities import Municipalities, Submission
from composting.forms import SkipForm


class TestMunicipalities(IntegrationTestBase):
    def setUp(self):
        super(TestMunicipalities, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()
        self.views = Municipalities(self.request)
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_index(self):
        self.request.context = self.municipality
        result = self.views.index()
        self.assertEqual(result['municipality'], self.municipality)

    def test_daily_waste_list(self):
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('pending', '1'),
            ('rejected', '1')
        ])
        result = self.views.daily_waste_list()
        self.assertEqual(result['municipality'], self.municipality)
        self.assertEqual(len(result['daily_wastes']), 1)

    def test_create_skip_get(self):
        self.request.context = self.municipality
        result = self.views.create_skip()
        self.assertIsInstance(result['form'].schema, SkipForm)

    def test_create_skip_post(self):
        self.request.context = self.municipality
        self.request.method = 'POST'
        self.request.POST = MultiDict([
            ('skip_type', 'A'),
            ('small_length', '20'),
            ('large_length', '30'),
            ('small_breadth', '16'),
            ('large_breadth', '20')
        ])
        num_skips = Skip.count()
        result = self.views.create_skip()
        self.assertEqual(Skip.count(), num_skips + 1)
        self.assertIsInstance(result, HTTPFound)
        skip = Skip.newest()
        self.assertEqual(
            result.location,
            self.request.route_url('skips', traverse=(skip.id, 'edit')))
        municipality = Municipality.get(Municipality.name == "Mukono")
        self.assertEqual(skip.municipality, municipality)

    def test_create_skip_invalid_post(self):
        self.request.context = self.municipality
        self.request.method = 'POST'
        self.request.POST = MultiDict([
            ('skip_type', 'A'),
            ('small_length', '20'),
            ('large_length', '30'),
            ('small_breadth', '16'),
            ('large_breadth', '')
        ])
        num_skips = Skip.count()
        result = self.views.create_skip()
        self.assertEqual(Skip.count(), num_skips)
        self.assertIsInstance(result['form'].schema, SkipForm)


class TestMunicipalitiesFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestMunicipalitiesFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_index(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id,))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_daily_waste_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'daily-waste'),
            _query={Submission.PENDING: '1', Submission.REJECTED: '1'})
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def _test_daily_waste_show(self):
        daily_waste_record = None
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'daily-waste'))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_create_skip_get(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'create-skip'))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)
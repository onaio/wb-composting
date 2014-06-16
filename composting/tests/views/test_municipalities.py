import datetime
from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid import testing

from composting.libs.utils import get_month_start_end
from composting.models import Municipality, Skip
from composting.views.municipalities import Municipalities
from composting.forms import SkipForm
from composting.tests.test_base import (
    IntegrationTestBase, FunctionalTestBase)


class TestMunicipalities(IntegrationTestBase):
    def setUp(self):
        super(TestMunicipalities, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()
        self.views = Municipalities(self.request)
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_list(self):
        result = self.views.list()
        self.assertIn('municipalities', result)

    def test_show(self):
        self.request.context = self.municipality
        result = self.views.show()
        self.assertEqual(result['municipality'], self.municipality)

    def test_monthly_density_list_returns_items_for_requested_period(self):
        # today's date for this test
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('period', '2014-01')
        ])
        result = self.views.monthly_density_list()
        self.assertEqual(len(result['items']), 3)

    def _test_monthly_density_list_use_current_date_when_no_date_requested(
            self):
        # todo: after adding an explicit date field, update its value to
        # today's date for this test
        self.request.context = self.municipality
        result = self.views.monthly_density_list()
        self.assertEqual(len(result['items']), 1)

    def test_monthly_density_list_returns_avg_of_none_if_no_items(self):
        # todo: after adding an explicit date field, update its value to
        # today's date for this test
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('month', '2011-01')
        ])
        result = self.views.monthly_density_list()
        self.assertIsNone(result['average_density'])

    def test_monthly_density_list_when_bad_date_requested(self):
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('period', '2014')
        ])
        result = self.views.monthly_density_list()
        self.assertIsInstance(result, HTTPBadRequest)

    def test_skips(self):
        self.request.context = self.municipality
        result = self.views.skips()
        self.assertEqual(
            sorted(result.keys()), sorted(['municipality', 'skips']))

    def test_create_skip_get(self):
        self.request.context = self.municipality
        result = self.views.create_skip()
        self.assertIsInstance(result['form'].schema, SkipForm)

    def test_create_skip_post(self):
        self.request.context = self.municipality
        self.request.method = 'POST'
        self.request.POST = MultiDict([
            ('skip_type', 'Z'),
            ('small_length', '20'),
            ('large_length', '30'),
            ('small_breadth', '16'),
            ('large_breadth', '20')
        ])
        num_skips = Skip.count()
        result = self.views.create_skip()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(Skip.count(), num_skips + 1)
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
            ('skip_type', 'Z'),
            ('small_length', '20'),
            ('large_length', '30'),
            ('small_breadth', '16'),
            ('large_breadth', '')
        ])
        num_skips = Skip.count()
        result = self.views.create_skip()
        self.assertEqual(Skip.count(), num_skips)
        self.assertIsInstance(result['form'].schema, SkipForm)

    def test_edit_profile_post(self):
        municipality_id = self.municipality.id
        self.request.context = self.municipality
        self.request.method = 'POST'
        self.request.POST = MultiDict([
            ('name', 'Mukono Municipality'),
            ('wheelbarrow_volume', '0.15'),
            ('box_volume', '0.3'),
            ('leachete_tank_length', '8.0'),
            ('leachete_tank_width', '8.0')
        ])
        result = self.views.edit_profile()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(
            result.location,
            self.request.route_url(
                'municipalities', traverse=(municipality_id, 'profile')))
        municipality = Municipality.get(Skip.id == municipality_id)
        self.assertEqual(municipality.name, "Mukono Municipality")

    def test_site_reports_sets_start_end_to_current_month_if_not_specified(
            self):
        self.request.context = self.municipality
        result = self.views.site_reports()
        start, end = get_month_start_end(datetime.date.today())
        # if end is beyond today's date, end with be set to today
        today = datetime.date.today()
        end = today if end > today else end
        self.assertEqual(start, result['start'])
        self.assertEqual(end, result['end'])

    def test_site_reports_sets_uses_specified_start_end(self):
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('start', '2014-06-12'),
            ('end',   '2014-06-13'),
        ])
        result = self.views.site_reports()
        start, end = datetime.date(2014, 6, 12), datetime.date(2014, 6, 13)
        self.assertEqual(start, result['start'])
        self.assertEqual(end, result['end'])

    def test_site_reports_raises_bad_request_if_bad_start(self):
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('start', '2014-06'),
            ('end',   '2014-06-15'),
        ])
        self.assertRaises(HTTPBadRequest, self.views.site_reports)

    def test_site_reports_raises_bad_request_if_bad_end(self):
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('start', '2014-06-15'),
            ('end',   '2014-06'),
        ])
        self.assertRaises(HTTPBadRequest, self.views.site_reports)

    def test_site_reports_sets_start_to_end_if_start_gt_end(self):
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('start', '2014-06-16'),
            ('end',   '2014-06-13'),
        ])
        result = self.views.site_reports()
        self.assertEqual(result['start'], datetime.date(2014, 6, 13))


class TestMunicipalitiesFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestMunicipalitiesFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_list_if_user_with_list_privileges(self):
        url = self.request.route_path(
            'municipalities', traverse=())
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_list_if_user_without_list_privileges(self):
        url = self.request.route_path(
            'municipalities', traverse=())
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_show(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id,))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_monthly_density_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'monthly-waste-density'))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_skips(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'skips'))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_create_skip_get(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'create-skip'))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_site_profile_get(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'profile'))
        result = self.testapp.get(url)
        self.assertEqual(result.status_code, 200)

    def test_list_monthly_waste_composition(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'monthly-solid-waste-composition'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_daily_rejects_landfilled_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'daily-rejects-landfilled'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_rejects_density_from_sieving_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'density-of-rejects-from-sieving'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_municipality_electricity_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'municipality-electricity-register'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_leachete_monthly_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'leachete-monthly-register'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_compost_sales_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'outgoing-compost-sales-register'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_compost_density_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'monthly-compost-density-register'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_monthly_rejects_composition_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'monthly-rejects-composition-from-sieving'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_daily_vehicle_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'daily-vehicle-data-register'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_site_reports(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'reports'))
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)
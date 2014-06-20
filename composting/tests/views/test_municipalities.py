import datetime
from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPForbidden
from pyramid import testing

from composting.libs.utils import get_month_start_end
from composting.models.user import User
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

    def test_list_when_has_list_permission(self):
        self.config.testing_securitypolicy(userid='admin', permissive=True)
        result = self.views.list()
        self.assertIn('municipalities', result)

    def test_list_when_has_not_list_permission_and_has_municipality(self):
        self.request.user = User(municipality=Municipality(id=1))
        self.config.testing_securitypolicy(userid='manager', permissive=False)
        result = self.views.list()
        self.assertIsInstance(result, HTTPFound)

    def test_list_when_has_not_list_permission_and_has_no_municipality(self):
        self.request.user = User()
        self.config.testing_securitypolicy(userid='manager', permissive=False)
        result = self.views.list()
        self.assertIsInstance(result, HTTPForbidden)

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
        municipality = Municipality.get(Municipality.id == municipality_id)
        self.assertEqual(municipality.name, "Mukono Municipality")

    def test_create_profile_post(self):
        initial_count = Municipality.count()
        self.request.method = 'POST'
        self.request.user = User()
        self.request.POST = MultiDict([
            ('name', 'Arua Compost Plant'),
            ('wheelbarrow_volume', '0.15'),
            ('box_volume', '0.3'),
            ('leachete_tank_length', '8.0'),
            ('leachete_tank_width', '8.0')
        ])
        result = self.views.create_profile()

        self.assertIsInstance(result, HTTPFound)

        final_count = Municipality.count()
        self.assertEqual(final_count, initial_count + 1)

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
            ('end', '2014-06-13'),
        ])
        result = self.views.site_reports()
        start, end = datetime.date(2014, 6, 12), datetime.date(2014, 6, 13)
        self.assertEqual(start, result['start'])
        self.assertEqual(end, result['end'])

    def test_site_reports_raises_bad_request_if_bad_start(self):
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('start', '2014-06'),
            ('end', '2014-06-15'),
        ])
        self.assertRaises(HTTPBadRequest, self.views.site_reports)

    def test_site_reports_raises_bad_request_if_bad_end(self):
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('start', '2014-06-15'),
            ('end', '2014-06'),
        ])
        self.assertRaises(HTTPBadRequest, self.views.site_reports)

    def test_site_reports_sets_start_to_end_if_start_gt_end(self):
        self.request.context = self.municipality
        self.request.GET = MultiDict([
            ('start', '2014-06-16'),
            ('end', '2014-06-13'),
        ])
        result = self.views.site_reports()
        self.assertEqual(result['start'], datetime.date(2014, 6, 13))


class TestMunicipalitiesFunctional(FunctionalTestBase):

    def setUp(self):
        super(TestMunicipalitiesFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_list(self):
        url = self.request.route_path(
            'municipalities', traverse=())
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_show(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id,))
        headers = self._login_user(1)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_monthly_density_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'monthly-waste-density'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_skips_when_admin_user(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'skips'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_skips_when_current_site_user(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'skips'))
        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_skips_when_other_site_user(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'skips'))
        # test that users with p:municipality-show:<id> for a different
        # municipality are denied
        headers = self._login_user(3)
        self.testapp.get(url, headers=headers, status=403)

    def test_create_skip_get_when_admin_user(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'create-skip'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_create_skip_get_when_current_site_user(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'create-skip'))
        headers = self._login_user(2)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_create_skip_get_when_other_site_user(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'create-skip'))
        headers = self._login_user(3)
        self.testapp.get(url, headers=headers, status=403)

    def test_site_profile_get_when_admin_user(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'profile'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_site_profile_get_when_current_site_user(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'profile'))
        headers = self._login_user(2)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_site_profile_get_when_other_site_user(self):
        url = self.request.route_path(
            'municipalities', traverse=(self.municipality.id, 'profile'))
        headers = self._login_user(3)
        self.testapp.get(url, headers=headers, status=403)

    def test_monthly_waste_composition_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'monthly-solid-waste-composition'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_daily_rejects_landfilled_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'daily-rejects-landfilled'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_rejects_density_from_sieving_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'density-of-rejects-from-sieving'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_municipality_electricity_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'municipality-electricity-register'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_leachete_monthly_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'leachete-monthly-register'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_compost_sales_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'outgoing-compost-sales-register'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_compost_density_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'monthly-compost-density-register'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_monthly_rejects_composition_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'monthly-rejects-composition-from-sieving'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_daily_vehicle_register_list(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id,
                      'daily-vehicle-data-register'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_site_reports(self):
        url = self.request.route_path(
            'municipalities',
            traverse=(self.municipality.id, 'reports'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

        # test that users with p:municipality-show:<id> permission are allowed
        headers = self._login_user(2)
        result = self.testapp.get(url, headers=headers)
        self.assertEqual(result.status_code, 200)

    def test_create_profile(self):
        url = self.request.route_path(
            'municipalities', traverse=('create'))
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

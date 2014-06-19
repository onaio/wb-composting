from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPForbidden
from pyramid import testing

from composting.models.user import User
from composting.models import Municipality
from composting.views.users import Users
from composting.tests.test_base import (
    IntegrationTestBase, FunctionalTestBase)


class TestUsers(IntegrationTestBase):
    def setUp(self):
        super(TestUsers, self).setUp()
        self.setup_test_data()
        self.request = testing.DummyRequest()
        self.views = Users(self.request)
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_toggle_doenst_allow_deactivating_own_account(self):
        user = User.get(User.username == 'admin')
        self.request.user = user
        self.request.context = user
        response = self.views.toggle_status()
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(
            response.location, self.request.route_url('users', traverse=()))

    def test_toggle_toggles_user_status(self):
        self.request.user = User.get(User.username == 'admin')
        self.request.context = User.get(User.username == 'manager')
        self.assertEqual(User.get(User.username == 'manager').active, True)
        response = self.views.toggle_status()
        user = User.get(User.username == 'manager')
        self.assertEqual(user.active, False)
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(
            response.location, self.request.route_url('users', traverse=()))

    def test_edit_user_post(self):
        user = User.get(User.username == 'admin')
        self.request.context = user
        self.request.method = 'POST'
        self.request.POST = MultiDict([
            ('group', 'sm'),
            ('municipality_id', '2')
        ])
        response = self.views.edit()
        user = User.get(User.username == 'admin')
        self.assertEqual(user.group, 'sm')
        self.assertEqual(user.municipality_id, '2')
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(
            response.location,
            self.request.route_url('users', traverse=(user.id, 'edit')))


class TestUsersFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestUsersFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_list_when_nema_user(self):
        url = self.request.route_path('users', traverse=())
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_list_when_municipality_user(self):
        url = self.request.route_path('users', traverse=())
        headers = self._login_user(2)
        self.testapp.get(url, headers=headers, status=403)

    def test_edit_when_nema_user(self):
        user = User.get(User.username == 'manager')
        url = self.request.route_path('users', traverse=(user.id, 'edit'))
        headers = self._login_user(1)
        self.testapp.get(url, headers=headers, status=200)

    def test_edit_when_municipality_user(self):
        user = User.get(User.username == 'manager')
        url = self.request.route_path('users', traverse=(user.id, 'edit'))
        headers = self._login_user(2)
        self.testapp.get(url, headers=headers, status=403)
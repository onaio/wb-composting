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


class TestUsersFunctional(FunctionalTestBase):
    def setUp(self):
        super(TestUsersFunctional, self).setUp()
        self.setup_test_data()
        self.municipality = Municipality.get(Municipality.name == "Mukono")

    def test_list(self):
        url = self.request.route_path('users', traverse=())
        headers = self._login_user(1)
        response = self.testapp.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
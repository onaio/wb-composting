from composting.models.user import User
from composting.tests.test_base import TestBase


class TestUser(TestBase):
    def setUp(self):
        super(TestUser, self).setUp()
        self.setup_test_data()

    def test_update(self):
        user = User.get(User.username == 'admin')
        user.update(group='sm', municipality_id=1)
        self.assertEqual(user.group, 'sm')
        self.assertEqual(user.municipality_id, 1)

    def test_update_when_wb_or_nema(self):
        user = User.get(User.username == 'manager')
        user.update(group='nema', municipality_id=1)
        self.assertIsNone(user.municipality_id)
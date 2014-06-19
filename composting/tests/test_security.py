import unittest
from pyramid import testing

from composting.security import NEMA, friendly_group_name


class TestSecurity(unittest.TestCase):
    def test_friendly_group_name(self):
        request = testing.DummyRequest()
        group_key = NEMA.key
        group_name = friendly_group_name(group_key, request)
        self.assertEqual(group_name, "NEMA")
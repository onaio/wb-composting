import unittest
import colander

from composting.models import Municipality, Skip
from composting.forms import SkipForm
from composting.forms.skip import UniqueSkipTypeValidator
from composting.tests.test_base import TestBase


class TestSkipForm(TestBase):
    def setUp(self):
        super(TestSkipForm, self).setUp()
        self.pstruct = {
            'skip_type': 'A',
            'small_length': '10',
            'large_length': '20',
            'small_breadth': '8',
            'large_breadth': '10'
        }

    def test_validates_valid_data(self):
        schema = SkipForm().bind(municipality_id=0)
        value = schema.deserialize(self.pstruct)
        self.assertEqual(
            value,
            {
                'small_length': 10.0,
                'skip_type': u'A',
                'small_breadth': 8.0,
                'large_length': 20.0,
                'large_breadth': 10.0
            })

    def test_validates_skip_type_single_alphanum(self):
        schema = SkipForm().bind(municipality_id=0)
        self.pstruct['skip_type'] = 'ABCD'
        self.assertRaises(colander.Invalid, schema.deserialize, self.pstruct)

    def test_validates_small_length_lt_large_length(self):
        schema = SkipForm().bind(municipality_id=0)
        self.pstruct['small_length'] = '30'
        self.assertRaises(colander.Invalid, schema.deserialize, self.pstruct)

    def test_validates_small_breadth_lt_large_breadth(self):
        schema = SkipForm().bind(municipality_id=0)
        self.pstruct['small_breadth'] = '20'
        self.assertRaises(colander.Invalid, schema.deserialize, self.pstruct)


class TestUniqueSkipTypeValidator(TestBase):
    def setUp(self):
        super(TestUniqueSkipTypeValidator, self).setUp()
        self.setup_test_data()

    def test_passes_for_new_if_skip_type_doesnt_exist(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        validator = UniqueSkipTypeValidator(municipality.id, None)
        validator.__call__({}, 'Z')

    def test_passes_for_existing_if_skip_type_doesnt_exist(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        skip_a = Skip.get(
            Skip.municipality == municipality, Skip.skip_type == 'A')
        validator = UniqueSkipTypeValidator(municipality.id, skip_a.id)
        validator.__call__({}, 'Z')

    def test_raises_invalid_for_new_if_skip_type_already_exists(self):
        municipality = Municipality.get(Municipality.name == "Mukono")
        validator = UniqueSkipTypeValidator(municipality.id, None)
        self.assertRaises(colander.Invalid, validator.__call__, {}, 'A')

    def test_raises_invalid_for_existing_if_skip_type_already_exists(self):
        """
        If the skip type exists in the municipality and its not the skip
        type we're trying to edit, raise
        """
        municipality = Municipality.get(Municipality.name == "Mukono")
        # use zero as the other skip id
        validator = UniqueSkipTypeValidator(municipality.id, 0)
        self.assertRaises(colander.Invalid, validator.__call__, {}, 'A')
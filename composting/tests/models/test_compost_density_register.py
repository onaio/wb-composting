from composting.models.municipality import Municipality
from composting.models.compost_density_register import CompostDensityRegister
from composting.tests.test_base import TestBase


class TestCompostDensityRegister(TestBase):
    def test_net_weight(self):
        compost_density = CompostDensityRegister(
            json_data={
                'filled_box_weight': '2.5',
                'empty_box_weight': '1.0'
            })
        self.assertEqual(compost_density.net_weight, 1.5)

    def test_density(self):
        municipality = Municipality(box_volume=0.125)
        compost_density = CompostDensityRegister(
            json_data={
                'filled_box_weight': '2.5',
                'empty_box_weight': '1.0'
            })
        self.assertEqual(compost_density.density(municipality), 12.0)
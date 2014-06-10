from composting.models.municipality import Municipality
from composting.models.leachete_monthly_register import LeacheteMonthlyRegister
from composting.tests.test_base import TestBase


class TestLeacheteMonthlyRegister(TestBase):
    def test_net_height(self):
        leachete_register = LeacheteMonthlyRegister(
            json_data={
                'before_pumping/fbHeight_be4_pumping': '12.3',
                'after_pumping/fbHeight_after_pumping': '5.6'
            })
        self.assertAlmostEqual(leachete_register.net_height, 6.7)

    def test_volume(self):
        leachete_register = LeacheteMonthlyRegister(
            json_data={
                'before_pumping/fbHeight_be4_pumping': '12.3',
                'after_pumping/fbHeight_after_pumping': '5.6'
            })
        municipality = Municipality(
            leachete_tank_length=4.0,
            leachete_tank_width=3.0)
        self.assertAlmostEqual(
            leachete_register.volume(municipality), 80.4)
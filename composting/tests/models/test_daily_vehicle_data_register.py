from composting.tests.test_base import TestBase

from composting.models.daily_vehicle_register import DailyVehicleDataRegister


class TestDailyVehicleDataRegister(TestBase):

    def test_fuel_purchased_retrieval(self):
        daily_vehicle_register = DailyVehicleDataRegister(
            json_data={
                "fuel_purchased_liters": "12.3",
                "fuel_purchased": "yes"
            })
        self.assertEqual(daily_vehicle_register.fuel_purchased, 12.3)

from composting.tests.test_base import IntegrationTestBase
from composting.models import Municipality, DailyWaste, Submission


class TestMunicipality(IntegrationTestBase):
    def test_update(self):
        m = Municipality(name="Test Municipal", box_volume=0.125,
                         wheelbarrow_volume=0.625, leachete_tank_length=5.0,
                         leachete_tank_width=5.0)
        m.update(name="Another Test Municipal", box_volume=0.3,
                 wheelbarrow_volume=0.15, leachete_tank_length=8.0,
                 leachete_tank_width=6.0)
        self.assertEqual(m.name, "Another Test Municipal")
        self.assertEqual(m.box_volume, 0.3)
        self.assertEqual(m.wheelbarrow_volume, 0.15)
        self.assertEqual(m.leachete_tank_length, 8.0)
        self.assertEqual(m.leachete_tank_width, 6.0)

    def test_num_daily_wastes_returns_cached_count_if_set(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        municipality._num_actionable_daily_wastes = 1000
        self.assertEqual(municipality.num_actionable_daily_wastes, 1000)

    def test_num_daily_wastes_returns_actual_count_if_not_cached(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        self.assertEqual(municipality.num_actionable_daily_wastes, 1)
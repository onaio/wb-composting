from composting.tests.test_base import IntegrationTestBase
from composting.models import Municipality, DailyWaste, Submission


class TestMunicipality(IntegrationTestBase):
    def test_test_get_register_records_with_criterion(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        results = municipality.get_register_records(
            DailyWaste, Submission.status == Submission.PENDING)
        self.assertEqual(len(results), 1)

    def test_get_register_records_on_daily_waste(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        results = municipality.get_register_records(DailyWaste)
        self.assertTrue(all([isinstance(r, DailyWaste) for r in results]))
        self.assertEqual(len(results), 3)

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
from composting.tests.test_base import TestBase
from composting.models.windrow_monitoring import WindrowMonitoring


class TestWindrowMonitoring(TestBase):

    def test_count_of_low_samples(self):
        windrow_monitor = WindrowMonitoring(
            json_data={
                WindrowMonitoring.OXYGEN_READING_1: '39',
                WindrowMonitoring.OXYGEN_READING_2: '20',
                WindrowMonitoring.OXYGEN_READING_3: '9',
                WindrowMonitoring.OXYGEN_READING_4: '0',
                WindrowMonitoring.OXYGEN_READING_5: '9.9'
            })
        self.assertEqual(windrow_monitor.count_of_low_samples(), 3)

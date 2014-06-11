from composting.models.compost_sales_register import CompostSalesRegister
from composting.tests.test_base import TestBase


class TestCompostSalesRegister(TestBase):
    def test_volume_returns_none_if_bagged(self):
        compost_sale = CompostSalesRegister(
            json_data={
                'bagged_compost': 'yes'
            })
        self.assertIsNone(compost_sale.volume)

    def test_returns_volume_if_not_bagged(self):
        compost_sale = CompostSalesRegister(
            json_data={
                'bagged_compost': 'no',
                'compost_length': '3.0',
                'compost_width': '4.0',
                'compost_height': '5.0'
            })
        self.assertEqual(compost_sale.volume, 60.0)
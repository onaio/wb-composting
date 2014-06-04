from composting.models.monthly_waste_composition import MonthlyWasteComposition
from composting.tests.test_base import TestBase


class TestMonthlyWasteComposition(TestBase):
    monthly_waste_compositions = [
        MonthlyWasteComposition(
            json_data={
                '_xform_id_string': 'monthly_waste_composition',
                'wood_products': '1.0',
                'paper_pulp': '2.0',
                'food_waste': '0.0',
                'garden_yard_waste': '0.8',
                'textiles': '0.6',
                'glass_plastics_metal': '1.3'
            }),
        MonthlyWasteComposition(
            json_data={
                '_xform_id_string': 'monthly_waste_composition',
                'wood_products': '0.8',
                'paper_pulp': '1.8',
                'food_waste': '0.4',
                'garden_yard_waste': '0.8',
                'textiles': '1.0',
                'glass_plastics_metal': '0.5'
            }),
    ]

    def test_total_waste(self):
        monthly_waste_composition = MonthlyWasteComposition(
            json_data={
                '_xform_id_string': 'monthly_waste_composition',
                'wood_products': '1.0',
                'paper_pulp': '2.0',
                'food_waste': '0.0',
                'garden_yard_waste': '0.8',
                'textiles': '0.6',
                'glass_plastics_metal': '1.3'
            })
        self.assertEqual(monthly_waste_composition.total_waste,
                         1.0 + 2.0 + 0.0 + 0.8 + 0.6 + +1.3)

    def test_total_by(self):
        total_wood_products = MonthlyWasteComposition.total_by(
            self.monthly_waste_compositions, 'wood_products')
        self.assertEqual(total_wood_products, 1.8)

    def test_get_total_waste_mean(self):
        total_waste_mean = MonthlyWasteComposition.get_total_waste_mean(
            self.monthly_waste_compositions)
        self.assertEqual((5.3 + 5.7) / 2, total_waste_mean)

    def test_get_total_waste_mean_when_no_records(self):
        total_waste_mean = MonthlyWasteComposition.get_total_waste_mean([])
        self.assertIsNone(total_waste_mean)

    def test_get_means(self):
        means = MonthlyWasteComposition.get_means(
            self.monthly_waste_compositions)
        self.assertEqual(means, {
            'wood_products': 0.9,
            'paper_pulp': 1.9,
            'food_waste': 0.2,
            'garden_yard_waste': 0.8,
            'textiles': 0.8,
            'glass_plastics_metal': 0.9
        })

    def test_get_means_when_no_records(self):
        means = MonthlyWasteComposition.get_means([])
        self.assertEqual(means, {
            'wood_products': None,
            'paper_pulp': None,
            'food_waste': None,
            'garden_yard_waste': None,
            'textiles': None,
            'glass_plastics_metal': None
        })

    def test_get_percentages(self):
        percentages = MonthlyWasteComposition.get_percentages(
            self.monthly_waste_compositions)
        # waste total == 11
        self.assertEqual(percentages, {
            'wood_products': 1.8/11,
            'paper_pulp': 3.8/11,
            'food_waste': 0.4/11,
            'garden_yard_waste': 1.6/11,
            'textiles': 1.6/11,
            'glass_plastics_metal': 1.8/11
        })

    def test_get_percentages_when_no_records(self):
        percentages = MonthlyWasteComposition.get_percentages([])
        # waste total == 11
        self.assertEqual(percentages, {
            'wood_products': None,
            'paper_pulp': None,
            'food_waste': None,
            'garden_yard_waste': None,
            'textiles': None,
            'glass_plastics_metal': None
        })
from zope.interface import implementer

from composting import constants
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class MonthlyWasteComposition(Submission):
    __mapper_args__ = {
        'polymorphic_identity': constants.MONTHLY_WASTE_COMPOSITION_FORM,
    }
    DATE_FIELD = 'month_year'
    DATE_FORMAT = '%Y-%m-%d'

    LIST_ACTION_NAME = 'monthly-solid-waste-composition'
    FORM_ID = "2220"

    # list of fields that contain weight values
    VALUE_FIELDS = ['wood_products', 'paper_pulp', 'food_waste',
                    'garden_yard_waste', 'textiles', 'glass_plastics_metal']

    @staticmethod
    def reduce_by_sum(accumulated, value):
        """
        Reduce the supplied float strings by summing them.
        """
        return accumulated + float(value)

    @property
    def total_waste(self):
        # build a list of values form teh list of fields
        values = [v for k, v in self.json_data.iteritems()
                  if k in MonthlyWasteComposition.VALUE_FIELDS]
        return reduce(self.reduce_by_sum, values, 0.0)

    @classmethod
    def total_by(cls, monthly_waste_compositions, key):
        """
        Get the total value by the specified key across the provided
        monthly_wastes
        """
        values = [s.json_data[key] for s in monthly_waste_compositions]
        return reduce(cls.reduce_by_sum, values, 0.0)

    @classmethod
    def waste_total(cls, monthly_waste_compositions):
        return reduce(
            lambda a, s: a + s.total_waste, monthly_waste_compositions, 0.0)

    @classmethod
    def get_total_waste_mean(cls, monthly_waste_compositions):
        if len(monthly_waste_compositions) == 0:
            return None

        total = cls.waste_total(monthly_waste_compositions)
        return total / len(monthly_waste_compositions)

    @classmethod
    def get_means(cls, monthly_waste_compositions):
        # for each value field, get the total then calculate the mean
        means = dict([(f, None) for f in cls.VALUE_FIELDS])
        if len(monthly_waste_compositions) == 0:
            return means

        for key in cls.VALUE_FIELDS:
            total = cls.total_by(monthly_waste_compositions, key)
            mean = total / len(monthly_waste_compositions)
            means[key] = mean
        return means

    @classmethod
    def get_percentages(cls, monthly_waste_compositions):
        percentages = dict([(f, None) for f in cls.VALUE_FIELDS])
        if len(monthly_waste_compositions) == 0:
            return percentages

        # get total waste
        waste_total = cls.waste_total(monthly_waste_compositions)
        for key in cls.VALUE_FIELDS:
            total = cls.total_by(monthly_waste_compositions, key)
            percentage = total / waste_total
            percentages[key] = percentage
        return percentages

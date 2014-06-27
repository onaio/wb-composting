from zope.interface import implementer
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class MonthlyRejectsComposition(Submission):
    XFORM_ID = 'monthly_composition_rejects_from_sieving'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'month_year'
    DATE_FORMAT = '%Y-%m-%d'
    TOTAL_MATURE_COMPOST_FIELD = 'total_mature_compost'

    LIST_ACTION_NAME = 'monthly-rejects-composition-from-sieving'

    def percentage(self, key):
        return float(self.json_data[key])\
            / float(self.json_data[self.TOTAL_MATURE_COMPOST_FIELD])

    def total_mature_compost_volume(self, municipality):
        from composting.models.compost_density_register import\
            CompostDensityRegister
        # volume = mass/density
        # find the monthly compost density for our month
        monthly_compost_density = CompostDensityRegister.get_by_date(self.date)
        if monthly_compost_density is None:
            return None
        return (float(self.json_data[self.TOTAL_MATURE_COMPOST_FIELD])
                /monthly_compost_density.density(municipality))
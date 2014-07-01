from zope.interface import implementer

from composting.constants import KGS_PER_TONNE
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
    SIEVED_COMPOST_FIELD = 'sieved_compost'

    LIST_ACTION_NAME = 'monthly-rejects-composition-from-sieving'

    def percentage(self, key):
        return float(self.json_data[key])\
            / float(self.json_data[self.TOTAL_MATURE_COMPOST_FIELD])

    def get_compost_density(self):
        from composting.models.compost_density_register import\
            CompostDensityRegister
        # find our municipality submission and hence our municipality
        municipality_submission = self.municipality_submission
        if municipality_submission is None:
            return None

        municipality = municipality_submission.municipality

        # find the monthly compost density for our month and municipality
        compost_density_record = CompostDensityRegister.get_by_date(
            self.date,
            municipality,
            CompostDensityRegister.status == Submission.APPROVED)
        if compost_density_record is None:
            return None

        return compost_density_record.density()

    def volume_of_mature_compost(self):
        # find the monthly compost density for our month and municipality
        monthly_compost_density = self.get_compost_density()
        if monthly_compost_density is None:
            return None

        # volume = mass/density
        return float(self.json_data[self.TOTAL_MATURE_COMPOST_FIELD])\
            / monthly_compost_density

    def can_approve(self, request):
        return super(MonthlyRejectsComposition, self).can_approve(request)\
            and self.volume_of_mature_compost() is not None

    def create_or_update_report(self):
        report = self.get_or_create_report()
        volume_of_mature_compost = self.volume_of_mature_compost()
        density_of_mature_compost = self.get_compost_density()/KGS_PER_TONNE
        conversion_factor = self.percentage(self.SIEVED_COMPOST_FIELD)
        report.report_json = {
            'volume_of_mature_compost': volume_of_mature_compost,
            'density_of_mature_compost': density_of_mature_compost,
            'conversion_factor': conversion_factor,
            'quantity_of_compost_produced': (volume_of_mature_compost
                                             * density_of_mature_compost
                                             * conversion_factor)
        }
        report.save()
        return report
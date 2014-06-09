from zope.interface import implementer
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class MonthlyRejectsDensity(Submission):
    XFORM_ID = 'monthly_density_rejects_from_sieving'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'month_year'
    DATE_FORMAT = '%Y-%m-%d'
    FILLED_BOX_WEIGHT_FIELD = 'filled_box_weight'
    EMPTY_BOX_WEIGHT_FIELD = 'empty_box_weight'

    LIST_ACTION_NAME = 'density-of-rejects-from-sieving'

    @property
    def net_weight(self):
        return float(self.json_data[self.FILLED_BOX_WEIGHT_FIELD])\
            - float(self.json_data[self.EMPTY_BOX_WEIGHT_FIELD])

    def density(self, municipality):
        # get the municipality for this submission
        box_volume = municipality.box_volume
        return self.net_weight/box_volume
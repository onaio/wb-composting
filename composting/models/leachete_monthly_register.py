from zope.interface import implementer
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class LeacheteMonthlyRegister(Submission):
    XFORM_ID = 'leachate_monthly_register'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'month_year'
    DATE_FORMAT = '%Y-%m-%d'
    HEIGHT_B4_PUMPING_FIELD = 'before_pumping/fbHeight_be4_pumping'
    HEIGHT_AF_PUMPING_FIELD = 'after_pumping/fbHeight_after_pumping'

    LIST_ACTION_NAME = 'leachete-monthly-register'

    @property
    def net_height(self):
        return float(self.json_data[self.HEIGHT_B4_PUMPING_FIELD])\
            - float(self.json_data[self.HEIGHT_AF_PUMPING_FIELD])

    def volume(self, municipality):
        return municipality.leachete_tank_length\
               * municipality.leachete_tank_width\
               * self.net_height
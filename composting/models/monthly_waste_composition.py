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
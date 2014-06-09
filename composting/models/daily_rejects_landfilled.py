from zope.interface import implementer
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class DailyRejectsLandfilled(Submission):
    XFORM_ID = 'register_daily_rejects_landfilled'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'date'
    DATE_FORMAT = '%Y-%m-%d'

    LIST_ACTION_NAME = 'daily-rejects-landfilled'
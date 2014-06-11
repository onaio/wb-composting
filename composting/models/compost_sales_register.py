from zope.interface import implementer
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class CompostSalesRegister(Submission):
    XFORM_ID = 'compost_sales_register'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'date'
    DATE_FORMAT = '%Y-%m-%d'

    LIST_ACTION_NAME = 'outgoing-compost-sales-register'
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
    IS_BAGGED_COMPOST_FIELD = 'bagged_compost'
    COMPOST_LENGTH_FIELD = 'compost_length'
    COMPOST_WIDTH_FIELD = 'compost_width'
    COMPOST_HEIGHT_FIELD = 'compost_height'

    LIST_ACTION_NAME = 'outgoing-compost-sales-register'

    @property
    def volume(self):
        if self.json_data[self.IS_BAGGED_COMPOST_FIELD] == 'yes':
            return None

        return float(self.json_data[self.COMPOST_LENGTH_FIELD])\
               * float(self.json_data[self.COMPOST_WIDTH_FIELD])\
               * float(self.json_data[self.COMPOST_HEIGHT_FIELD])
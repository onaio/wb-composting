from zope.interface import implementer
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class DailyVehicleDataRegister(Submission):
    XFORM_ID = 'daily_vehicle_data_register'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'date'
    DATE_FORMAT = '%Y-%m-%d'

    LIST_ACTION_NAME = 'daily-vehicle-data-register'
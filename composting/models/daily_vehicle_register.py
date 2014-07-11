from zope.interface import implementer
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class DailyVehicleDataRegister(Submission):
    XFORM_ID = 'daily_vehicle_data_register'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    # form fields
    DATE_FIELD = 'date'
    DATE_FORMAT = '%Y-%m-%d'

    LIST_ACTION_NAME = 'daily-vehicle-data-register'

    FUEL_PURCHASED_FLAG = 'fuel_purchased'
    FUEL_PURCHASED_LTRS = 'fuel_purchased_liters'
    FORM_ID = "1580"

    _fuel = None

    @property
    def fuel_purchased(self):
        """
        Retrieve the amount of fuel used by the wee loader
        """
        if self._fuel is not None:
            return self._fuel

        if self.json_data[self.FUEL_PURCHASED_FLAG] == 'yes':
            self._fuel = float(self.json_data[self.FUEL_PURCHASED_LTRS])

        return self._fuel

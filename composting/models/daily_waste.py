from zope.interface import implementer
from sqlalchemy.orm.exc import NoResultFound
from dashboard.libs.utils import date_string_to_time

from composting import constants
from composting.models.base import ModelFactory
from composting.models.submission import ISubmission, Submission
from composting.models.monthly_density import MonthlyDensity


@implementer(ISubmission)
class DailyWaste(Submission):
    __mapper_args__ = {
        'polymorphic_identity': constants.DAILY_WASTE_REGISTER_FORM,
    }

    # form fields
    DATE_FIELD = 'datetime'
    COMPRESSOR_TRUCK = 'compressor_truck'
    VOLUME = 'volume'
    SKIP_TYPE = 'skip_type'
    WASTE_HEIGHT = 'waste_height'

    # list url suffix
    LIST_URL_SUFFIX = 'daily-waste'

    # cached values
    _volume = None
    _monthly_density = None

    @property
    def __name__(self):
        return self.id

    @__name__.setter
    def __name__(self, value):
        self.id = value

    @property
    def volume(self):
        """
        Get the volume of the compost

        if its a compressor truck, return the raw value of volume, otherwise
        return the skip types cross sectional area * waste height
        """
        if self._volume is not None:
            return self._volume

        if self.json_data[self.COMPRESSOR_TRUCK] == 'yes':
            self._volume = float(self.json_data[self.VOLUME])
        else:
            try:
                skip_type = self.json_data[self.SKIP_TYPE]
                skip = self.municipality_submission.get_skip(skip_type)
            except NoResultFound:
                self._volume = None
            else:
                self._volume = skip.cross_sectional_area * float(
                    self.json_data[self.WASTE_HEIGHT])
        return self._volume

    @property
    def time(self):
        # todo: stick to one field name likely date
        return date_string_to_time(self.json_data[self.DATE_FIELD])

    @property
    def monthly_density(self):
        self._monthly_density = (
            self._monthly_density
            or MonthlyDensity.get_average_density(self.date))
        return self._monthly_density

    @property
    def tonnage(self):
        monthly_density = self.monthly_density
        volume = self.volume
        if monthly_density is not None and volume is not None:
            return monthly_density * volume
        else:
            return None


class DailyWasteFactory(ModelFactory):
    def __getitem__(self, item):
        try:
            record = DailyWaste.get(DailyWaste.id == item)
        except NoResultFound:
            raise KeyError
        else:
            record.__name__ = item
            record.__parent__ = self
            return record
from zope.interface import implementer
from sqlalchemy.orm.exc import NoResultFound
from dashboard.libs.utils import date_string_to_time

from composting import constants
from composting.models.base import ModelFactory, DBSession
from composting.models.submission import ISubmission, Submission


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
        if self.json_data[self.COMPRESSOR_TRUCK] == 'yes':
            return float(self.json_data[self.VOLUME])
        else:
            try:
                skip_type = self.json_data[self.SKIP_TYPE]
                skip = self.municipality_submission.get_skip(skip_type)
            except NoResultFound:
                return None
            else:
                return skip.cross_sectional_area * float(
                    self.json_data[self.WASTE_HEIGHT])

    @property
    def time(self):
        # todo: stick to one field name likely date
        return date_string_to_time(self.json_data[self.DATE_FIELD])


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
from zope.interface import implementer

from sqlalchemy.orm.exc import NoResultFound

from dashboard.libs.utils import (
    date_string_to_date, date_string_to_time, date_string_to_month)

from composting import constants
from composting.models.submission import Submission, ISubmission
from composting.models.municipality_submission import MunicipalitySubmission


@implementer(ISubmission)
class MonthlyDensity(Submission):
    __mapper_args__ = {
        'polymorphic_identity': constants.MONTHLY_WASTE_DENSITY_FORM,
    }

    COMPRESSOR_TRUCK_FIELD = 'compressor_truck'
    VOLUME_FIELD = 'volume'
    SKIP_TYPE_FIELD = 'skip_type'
    WASTE_HEIGHT_FIELD = 'waste_height'
    FILLED_WEIGHT_FIELD = 'filled_weight'
    EMPTY_WEIGHT_FIELD = 'empty_weight'

    # list url suffix
    LIST_URL_SUFFIX = 'monthly-waste-density'

    @classmethod
    def date_from_json(cls, json_data):
        return date_string_to_date(
            json_data[cls.DATE_FIELD], cls.DATE_FORMAT)

    @property
    def time(self):
        # todo: stick to one convention for the name likely date
        return date_string_to_time(
            self.json_data[self.DATE_FIELD])

    @property
    def month(self):
        return date_string_to_month(
            self.json_data[self.DATE_FIELD])

    @property
    def volume(self):
        """
        Get the volume of the compost

        if its a compressor truck, return the raw value of volume, otherwise
        return the skip types cross sectional area * waste height
        """
        if self.json_data[self.COMPRESSOR_TRUCK_FIELD] == 'yes':
            return float(self.json_data[self.VOLUME_FIELD])
        else:
            try:
                skip_type = self.json_data[self.SKIP_TYPE_FIELD]
                skip = self.municipality_submission.get_skip(skip_type)
            except NoResultFound:
                return None
            else:
                return skip.cross_sectional_area * float(
                    self.json_data[self.WASTE_HEIGHT_FIELD])

    @property
    def net_weight(self):
        return (
            float(self.json_data[self.FILLED_WEIGHT_FIELD])
            - float(self.json_data[self.EMPTY_WEIGHT_FIELD]))

    @property
    def density(self):
        return self.net_weight / self.volume

    @classmethod
    def get_average_density(cls, monthly_densities):
        if len(monthly_densities) < 1:
            raise ValueError("You must provide at least 1 monthly density")
        return (reduce(
            lambda accum, x: x.density + accum, monthly_densities, 0)
                / len(monthly_densities))
from zope.interface import implementer

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey
)
from sqlalchemy.orm import relationship

from dashboard.libs.utils import date_string_to_date, date_string_to_time

from composting.models.base import Base, ModelFactory, DBSession
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class MonthlyDensity(Submission):
    __mapper_args__ = {
        'polymorphic_identity': 'monthly_density',
    }
    # TODO: make relationship
    municipality_id = 1

    COMPRESSOR_TRUCK_FIELD = 'compressor_truck'
    VOLUME_FIELD = 'volume'
    SKIP_TYPE_FIELD = 'skip_type'
    WASTE_HEIGHT_FIELD = 'waste_height'
    FILLED_WEIGHT_FIELD = 'filled_weight'
    EMPTY_WEIGHT_FIELD = 'empty_weight'

    @property
    def date(self):
        # todo: stick to one convention for the name likely date
        return date_string_to_date(
            self.json_data.get(
                'date', self.json_data.get('dateTime')))

    @property
    def time(self):
        # todo: stick to one convention for the name likely date
        return date_string_to_time(
            self.json_data.get(
                'date', self.json_data.get('dateTime')))

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
                skip = self.get_skip()
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

    def get_skip(self):
        """
        Get the skip associated with this waste register
        """
        # TODO: make a pure function that takes a municipality/id and skip type
        from composting.models import Skip
        return DBSession.query(Skip)\
            .filter(
                Skip.skip_type == self.json_data[self.SKIP_TYPE_FIELD],
                Skip.municipality_id == self.municipality_id).one()
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey
)
from sqlalchemy.orm import relationship

from dashboard.libs.utils import date_string_to_date, date_string_to_time

from composting.models.base import Base, ModelFactory, DBSession
from composting.models import Submission


class DailyWaste(Base):
    __tablename__ = 'daily_wastes'
    id = Column(Integer, primary_key=True)
    submission_id = Column(
        Integer, ForeignKey('submissions.id'), nullable=False)
    submission = relationship('Submission')
    # todo: implement relationship
    municipality_id = 1

    # form fields
    COMPRESSOR_TRUCK = 'compressor_truck'
    VOLUME = 'volume'
    SKIP_TYPE = 'skip_type'
    WASTE_HEIGHT = 'waste_height'

    @property
    def __name__(self):
        return self.id

    @__name__.setter
    def __name__(self, value):
        self.id = value

    def can_approve(self, request):
        """
        Anyone with permissions can approve if pending
        """
        return (self.submission.status == Submission.PENDING
                or (self.submission.status == Submission.REJECTED
                    and request.GET.get('role') != 'nema'))

    def can_reject(self, request):
        """
        Only NEMA and WB can reject and only after it been approved
        """
        return (self.submission.status == Submission.APPROVED
                and request.GET.get('role') == 'nema')

    def can_unapprove(self, request):
        """
        Only the site manager can un-approve
        """
        return self.submission.status == Submission.APPROVED

    @property
    def volume(self):
        """
        Get the volume of the compost

        if its a compressor truck, return the raw value of volume, otherwise
        return the skip types cross sectional area * waste height
        """
        if self.submission.json_data[self.COMPRESSOR_TRUCK] == 'yes':
            return float(self.submission.json_data[self.VOLUME])
        else:
            try:
                skip = self.get_skip()
            except NoResultFound:
                return None
            else:
                return skip.cross_sectional_area * float(
                    self.submission.json_data[self.WASTE_HEIGHT])

    def get_skip(self):
        """
        Get the skip associated with this waste register
        """
        from composting.models import Skip
        return DBSession.query(Skip)\
            .filter(
                Skip.skip_type == self.submission.json_data[self.SKIP_TYPE],
                Skip.municipality_id == self.municipality_id).one()

    @property
    def tonnage(self):
        pass

    @property
    def date(self):
        return date_string_to_date(self.submission.json_data['date'])

    @property
    def time(self):
        return date_string_to_time(self.submission.json_data['date'])


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
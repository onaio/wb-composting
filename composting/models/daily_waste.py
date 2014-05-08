from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey
)
from sqlalchemy.orm import relationship

from composting.libs.utils import translation_string_factory as _
from composting.models.base import Base, ModelFactory
from composting.models import Submission


class DailyWaste(Base):
    __tablename__ = 'daily_wastes'
    id = Column(Integer, primary_key=True)
    submission_id = Column(
        Integer, ForeignKey('submissions.id'), nullable=False)
    submission = relationship('Submission')

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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey
)
from sqlalchemy.orm import relationship

from composting.models.base import Base, ModelFactory


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
from sqlalchemy import (
    Column,
    Integer,
    Date,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import (
    relationship,
)

from wbcomposting.models.base import Base


class DailyWaste(Base):
    __tablename__ = 'daily_wastes'
    id = Column(Integer, primary_key=True)
    submission_id = Column(
        Integer, ForeignKey('submissions.id'), nullable=False)
    submission = relationship('Submission')
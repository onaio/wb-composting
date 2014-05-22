from sqlalchemy import (
    Column,
    Integer,
    Date,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship

from composting.models.base import Base, DBSession


class MunicipalitySubmission(Base):
    """
    Base class for all submissions that are linked to a municipality
    """
    __tablename__ = 'municipality_submissions'
    __table_args__ = (
        Index('ix_municipality_id_submission_id', 'municipality_id',
              'submission_id', unique=True),)
    submission_id = Column(
        Integer, ForeignKey('submissions.id'), primary_key=True,
        nullable=False)
    submission = relationship('Submission')
    municipality_id = Column(
        Integer, ForeignKey('municipalities.id'), nullable=False)
    municipality = relationship('Municipality')
    date = Column(Date, nullable=False)

    @classmethod
    def get_items(cls, municipality, submission_subclass, *criterion):
        return DBSession.query(cls, submission_subclass)\
            .filter(
                cls.submission_id == submission_subclass.id,
                cls.municipality == municipality, *criterion)\
            .all()
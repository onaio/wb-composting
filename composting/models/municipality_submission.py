from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound

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
    submission = relationship(
        'Submission',
        backref=backref('municipality_submission', uselist=False))
    municipality_id = Column(
        Integer, ForeignKey('municipalities.id'), nullable=False)
    municipality = relationship('Municipality')

    @classmethod
    def get_items_query(cls, municipality, submission_subclass, *criterion):
        return DBSession.query(cls, submission_subclass)\
            .filter(
                cls.submission_id == submission_subclass.id,
                cls.municipality == municipality,
                *criterion)

    @classmethod
    def get_items(cls, municipality, submission_subclass, *criterion):
        return cls.get_items_query(
            municipality, submission_subclass, *criterion)\
            .all()

    def get_skip(self, skip_type):
        """
        Get the skip associated with this municipality and of the specified
        type
        """
        skip = self.municipality.get_skip(skip_type)
        if skip is None:
            raise NoResultFound("Skip type '{}' does not exist in this"
                                " municipality".format(skip_type))
        else:
            return skip
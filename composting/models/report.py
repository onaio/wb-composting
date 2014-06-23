from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship, backref


from composting.models.base import Base


class Report(Base):
    __tablename__ = 'reports'

    submission_id = Column(
        Integer, ForeignKey('submissions.id'), primary_key=True,
        nullable=False)
    report_json = Column(JSON, nullable=False)
    submission = relationship(
        'Submission', backref=backref('report', uselist=False))
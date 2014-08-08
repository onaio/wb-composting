from composting.models.base import DBSession
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Date,
    and_
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import extract


from composting.models.base import Base


class SiteReport(Base):
    __tablename__ = 'site_reports'

    id = Column(Integer, primary_key=True)
    report_date = Column(Date, nullable=False, server_default='1970-01-01')
    report_json = Column(JSON, nullable=False)
    municipality_id = Column(
        Integer, ForeignKey('municipalities.id'), nullable=False)
    municipality = relationship('Municipality')

    @classmethod
    def get_report_by_date(cls, date, municipality):
        return DBSession.query(SiteReport)\
            .filter(and_(
                extract('month', SiteReport.report_date) == date.month,
                extract('year', SiteReport.report_date) == date.year,
                SiteReport.municipality == municipality)).one()

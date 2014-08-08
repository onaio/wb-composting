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
VOLUME = 'm3'
DENSITY = 'Ton/m3'
TONNES = 'Tonnes'
NUMBER = 'No.'
AVERAGE = 'average'
DISTANCE = 'kms'
LITRES = 'litres'
ELECTRICITY = 'MWh'
RATIO = '%'


class SiteReport(Base):
    __tablename__ = 'site_reports'

    REPORT_VALUE_UNITS = {
        'volume_of_msw_processed': VOLUME,
        'density_of_msw': DENSITY,
        'quantity_of_msw_processed': TONNES,
        'num_trucks_delivered_msw': NUMBER,
        'volume_of_mature_compost': VOLUME,
        'density_of_mature_compost': DENSITY,
        'conversion_factor_mature_to_sieved': AVERAGE,
        'quantity_of_compost_produced': TONNES,
        'quantity_of_compost_sold': TONNES,
        'vehicle_count': NUMBER,
        'average_distance': DISTANCE,
        'volume_of_rejects_from_sieving': TONNES,
        'density_of_rejects_from_sieving': DENSITY,
        'quantity_of_rejects_from_sieving_landfilled': TONNES,
        'total_windrow_samples': NUMBER,
        'low_windrow_sample_count': NUMBER,
        'fuel_consumption': LITRES,
        'electricity_consumption': ELECTRICITY,
        'leachete_volume_accumulated': VOLUME
    }

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

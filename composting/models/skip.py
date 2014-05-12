from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    Index,
)
from sqlalchemy.orm import relationship

from composting.models.base import DBSession, Base, ModelFactory


class Skip(Base):
    __tablename__ = 'skips'
    __tableargs__ = (
        Index('ix_skip_type_municipality_id', 'skip_type', 'municipality_id',
              unique=True),)
    id = Column(Integer, primary_key=True)
    skip_type = Column(String(2), nullable=False)
    municipality_id = Column(
        Integer, ForeignKey('municipalities.id'), nullable=False)
    municipality = relationship('Municipality')
    small_length = Column(Float, nullable=False)
    large_length = Column(Float, nullable=False)
    small_breadth = Column(Float, nullable=False)
    large_breadth = Column(Float, nullable=False)

    @property
    def cross_sectional_area(self):
        return ((
                   (self.small_length + self.large_length)
                   * (self.small_breadth + self.large_breadth))\
               / 4)
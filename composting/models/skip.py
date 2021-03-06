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
    __table_args__ = (
        Index('ix_skip_type_municipality_id', 'skip_type', 'municipality_id',
              unique=True),)
    id = Column(Integer, primary_key=True)
    municipality_id = Column(
        Integer, ForeignKey('municipalities.id'), nullable=False)
    municipality = relationship('Municipality')
    skip_type = Column(String(2), nullable=False)
    small_length = Column(Float, nullable=False)
    large_length = Column(Float, nullable=False)
    small_breadth = Column(Float, nullable=False)
    large_breadth = Column(Float, nullable=False)

    @property
    def cross_sectional_area(self):
        return ((
                (self.small_length + self.large_length)
                * (self.small_breadth + self.large_breadth))
                / 4)

    @property
    def appstruct(self):
        return {
            'skip_type': self.skip_type,
            'small_length': self.small_length,
            'large_length': self.large_length,
            'small_breadth': self.small_breadth,
            'large_breadth': self.large_breadth
        }

    def update(
            self, skip_type, small_length, large_length, small_breadth,
            large_breadth):
        self.skip_type = skip_type
        self.small_length = small_length
        self.large_length = large_length
        self.small_breadth = small_breadth
        self.large_breadth = large_breadth


class SkipFactory(ModelFactory):
    def __getitem__(self, item):
        try:
            record = Skip.get(Skip.id == item)
        except NoResultFound:
            raise KeyError
        else:
            record.__name__ = item
            record.__parent__ = self
            return record
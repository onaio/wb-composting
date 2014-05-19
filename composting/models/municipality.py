from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    or_
)
from sqlalchemy.orm import contains_eager

from composting.models.base import DBSession, Base, ModelFactory
from composting.models.daily_waste import Submission
from composting.models.daily_waste import DailyWaste
from composting.models.skip import Skip


class Municipality(Base):
    __tablename__ = 'municipalities'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    box_volume = Column(Float, nullable=False, server_default='0.125')
    wheelbarrow_volume = Column(Float, nullable=False, server_default='0.625')
    leachete_tank_length = Column(Float, nullable=False, server_default='5.0')
    leachete_tank_width = Column(Float, nullable=False, server_default='5.0')

    _num_daily_wastes = None

    #def __getitem__(self, item):
    #    try:
    #        submission = Submission.get(Submission.id == item)
    #    except NoResultFound:
    #        raise KeyError
    #    else:
    #        submission.__name__ = item
    #        submission.__parent__ = self
    #        return submission

    def get_register_records_query(self, register_class, *criterion):
        """
        Get records filtered by specified criterion from `register_class`
        eager loading from submissions
        """
        return DBSession.query(register_class)\
            .join(register_class.submission)\
            .filter(*criterion)\
            .options(contains_eager(register_class.submission))

    def get_register_records(self, register_class, *criterion):
        """
        Get records filtered by specified criterion from `register_class`
        eager loading from submissions
        """
        return self.get_register_records_query(register_class, *criterion)\
            .all()

    @property
    def num_daily_wastes(self):
        self._num_daily_wastes = self._num_daily_wastes\
            or self.get_register_records_query(
                DailyWaste,
                or_(
                    Submission.status == Submission.PENDING,
                    Submission.status == Submission.REJECTED))\
            .count()
        return self._num_daily_wastes

    def get_skips(self, *criterion):
        return DBSession.query(Skip)\
            .filter(Skip.municipality == self, *criterion)\
            .all()

    @property
    def appstruct(self):
        return {
            'name': self.name,
            'box_volume': self.box_volume,
            'wheelbarrow_volume': self.wheelbarrow_volume,
            'leachete_tank_length': self.leachete_tank_length,
            'leachete_tank_width': self.leachete_tank_width
        }

    def update(
            self, name, box_volume, wheelbarrow_volume, leachete_tank_length,
            leachete_tank_width):
        self.name = name
        self.box_volume = box_volume
        self.wheelbarrow_volume = wheelbarrow_volume
        self.leachete_tank_length = leachete_tank_length
        self.leachete_tank_width = leachete_tank_width

    def url(self, request, action=None):
        traverse = (self.id, action) if action else (self.id,)
        return request.route_url(
            'municipalities', traverse=traverse)


class MunicipalityFactory(ModelFactory):
    def __getitem__(self, item):
        try:
            record = Municipality.get(Municipality.id == item)
        except NoResultFound:
            raise KeyError
        else:
            record.__name__ = item
            record.__parent__ = self
            return record
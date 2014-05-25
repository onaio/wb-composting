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
from composting.models.submission import Submission
from composting.models.daily_waste import DailyWaste
from composting.models.monthly_density import MonthlyDensity
from composting.models.skip import Skip
from composting.models.municipality_submission import (
            MunicipalitySubmission)


class Municipality(Base):
    __tablename__ = 'municipalities'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    box_volume = Column(Float, nullable=False, server_default='0.125')
    wheelbarrow_volume = Column(Float, nullable=False, server_default='0.625')
    leachete_tank_length = Column(Float, nullable=False, server_default='5.0')
    leachete_tank_width = Column(Float, nullable=False, server_default='5.0')

    actionable_criterion = criterion = or_(
        Submission.status == Submission.PENDING,
        Submission.status == Submission.REJECTED)
    _num_actionable_daily_wastes = None
    _num_actionable_monthly_waste = None

    factories = {
        #'monthly-waste-density': MonthlyDensity
        'daily-waste': DailyWaste
    }

    def __getitem__(self, item):
        try:
            model = self.factories[item](self.request)
        except KeyError:
            raise
        else:
            model.__name__ = str(item)
            model.__parent__ = self
            return model

    @property
    def num_actionable_daily_wastes(self):
        self._num_actionable_daily_wastes = self._num_actionable_daily_wastes\
            or MunicipalitySubmission.get_items_query(
                self, DailyWaste, self.actionable_criterion)\
            .count()
        return self._num_actionable_daily_wastes

    @property
    def num_actionable_monthly_waste(self):
        self._num_actionable_monthly_waste = (
            self._num_actionable_monthly_waste
            or MunicipalitySubmission.get_items_query(
                self, MonthlyDensity, self.actionable_criterion).count())
        return self._num_actionable_monthly_waste

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
            record.request = self.request
            return record
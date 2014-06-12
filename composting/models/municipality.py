from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    or_
)

from composting.models.base import DBSession, Base, ModelFactory
from composting.models.submission import Submission
from composting.models.daily_waste import DailyWaste
from composting.models.monthly_density import MonthlyDensity
from composting.models.monthly_waste_composition import MonthlyWasteComposition
from composting.models.skip import Skip
from composting.models.municipality_submission import (
    MunicipalitySubmission)
from composting.models.windrow_monitoring import (
    WindrowMonitoring, WindrowMonitoringFactory)
from composting.models.daily_rejects_landfilled import DailyRejectsLandfilled
from composting.models.monthly_rejects_density import MonthlyRejectsDensity
from composting.models.electricity_register import ElectricityRegister
from composting.models.leachete_monthly_register import LeacheteMonthlyRegister
from composting.models.compost_sales_register import CompostSalesRegister
from composting.models.compost_density_register import CompostDensityRegister
from composting.models.monthly_rejects_composition import (
    MonthlyRejectsComposition)
from composting.models.daily_vehicle_register import DailyVehicleDataRegister


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
    _num_actionable_monthly_waste_composition = None
    _num_actionable_windrow_monitoring = None
    _num_actionable_daily_rejects_landfilled = None
    _num_actionable_monthly_rejects_density = None
    _num_actionable_electricity_register = None
    _num_actionable_leachete_monthly_register = None
    _num_actionable_compost_sales_register = None
    _num_actionable_compost_density_register = None
    _num_actionable_monthly_rejects_composition = None
    _num_actionable_daily_vehicle_register = None

    factories = {
        DailyWaste.LIST_ACTION_NAME: DailyWaste,
        WindrowMonitoring.LIST_ACTION_NAME: WindrowMonitoring,
        'windrows': WindrowMonitoringFactory,
        DailyRejectsLandfilled.LIST_ACTION_NAME: DailyRejectsLandfilled,
        MonthlyRejectsDensity.LIST_ACTION_NAME: MonthlyRejectsDensity,
        ElectricityRegister.LIST_ACTION_NAME: ElectricityRegister,
        LeacheteMonthlyRegister.LIST_ACTION_NAME: LeacheteMonthlyRegister,
        CompostDensityRegister.LIST_ACTION_NAME: CompostDensityRegister,
        CompostSalesRegister.LIST_ACTION_NAME: CompostSalesRegister,
        MonthlyRejectsComposition.LIST_ACTION_NAME: MonthlyRejectsComposition,
        DailyVehicleDataRegister.LIST_ACTION_NAME: DailyVehicleDataRegister
    }

    def __getitem__(self, item):
        try:
            klass = self.factories[item]
        except KeyError:
            raise
        else:
            model = klass(self.request)
            model.__name__ = str(item)
            model.__parent__ = self
            return model

    def actionable_items_count(self, submission_subclass):
        return MunicipalitySubmission.get_items_query(
            self, submission_subclass, self.actionable_criterion)\
            .count()

    @property
    def num_actionable_daily_wastes(self):
        self._num_actionable_daily_wastes = self._num_actionable_daily_wastes\
            or self.actionable_items_count(DailyWaste)
        return self._num_actionable_daily_wastes

    @property
    def num_actionable_monthly_waste(self):
        self._num_actionable_monthly_waste = (
            self._num_actionable_monthly_waste
            or self.actionable_items_count(MonthlyDensity))
        return self._num_actionable_monthly_waste

    @property
    def num_actionable_monthly_waste_composition(self):
        self._num_actionable_monthly_waste_composition = (
            self._num_actionable_monthly_waste_composition
            or self.actionable_items_count(MonthlyWasteComposition))
        return self._num_actionable_monthly_waste_composition

    @property
    def num_actionable_windrow_monitoring(self):
        self._num_actionable_windrow_monitoring = (
            self._num_actionable_windrow_monitoring
            or self.actionable_items_count(WindrowMonitoring))
        return self._num_actionable_windrow_monitoring

    @property
    def num_actionable_daily_rejects_landfilled(self):
        self._num_actionable_daily_rejects_landfilled = (
            self._num_actionable_daily_rejects_landfilled
            or self.actionable_items_count(DailyRejectsLandfilled))
        return self._num_actionable_daily_rejects_landfilled

    @property
    def num_actionable_monthly_rejects_density(self):
        self._num_actionable_monthly_rejects_density = (
            self._num_actionable_monthly_rejects_density
            or self.actionable_items_count(MonthlyRejectsDensity))
        return self._num_actionable_monthly_rejects_density

    @property
    def num_actionable_electricity_register(self):
        self._num_actionable_electricity_register = (
            self._num_actionable_electricity_register
            or self.actionable_items_count(ElectricityRegister))
        return self._num_actionable_electricity_register

    @property
    def num_actionable_leachete_monthly_register(self):
        self._num_actionable_leachete_monthly_register = (
            self._num_actionable_leachete_monthly_register
            or self.actionable_items_count(LeacheteMonthlyRegister))
        return self._num_actionable_leachete_monthly_register

    @property
    def num_actionable_compost_sales_register(self):
        self._num_actionable_compost_sales_register = (
            self._num_actionable_compost_sales_register
            or self.actionable_items_count(CompostSalesRegister))
        return self._num_actionable_compost_sales_register

    @property
    def num_actionable_compost_density_register(self):
        self._num_actionable_compost_density_register = (
            self._num_actionable_compost_density_register
            or self.actionable_items_count(CompostDensityRegister))
        return self._num_actionable_compost_density_register

    @property
    def num_actionable_monthly_rejects_composition(self):
        self._num_actionable_monthly_rejects_composition = (
            self._num_actionable_monthly_rejects_composition
            or self.actionable_items_count(MonthlyRejectsComposition))
        return self._num_actionable_monthly_rejects_composition

    @property
    def num_actionable_daily_vehicle_register(self):
        self._num_actionable_daily_vehicle_register = (
            self._num_actionable_daily_vehicle_register
            or self.actionable_items_count(DailyVehicleDataRegister))
        return self._num_actionable_daily_vehicle_register

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
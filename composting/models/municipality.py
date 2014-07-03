from pyramid.security import Allow
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    or_,
    and_
)
from sqlalchemy.sql.functions import sum as sqla_sum, func

from composting import security
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
from composting.models.report import Report


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

    # dict cache of skips with the skip type as the key
    _skips = {}

    def __acl__(self):
        # users who have the p:municipality-edit permission and the
        # p:municipality-show:<id>
        # in their effective principal's def can edit and show
        return [
            (Allow, security.MUNICIPALITY_SHOW_ANY.key, 'show'),
            (Allow, security.MUNICIPALITY_SHOW_OWN.key.format(
                self.id), 'show'),
            (Allow, security.MUNICIPALITY_EDIT_ANY.key, 'edit'),
            (Allow, security.MUNICIPALITY_EDIT_OWN.key.format(self.id), 'edit')
        ]

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

    def get_report_query(
            self, submission_subclass, start_date, end_date, *columns):
        """
        Build a report query that takes into account the current municipality,
        the period and the target xform_id
        :param submission_subclass: A subclass of Submission e.g. DailyWaste
        :param start_date: reporting start date
        :param end_date: reporting end date
        :param columns: for e.g. sums, the aggregate column defs
        :return: query object
        """
        return DBSession\
            .query(*columns)\
            .join(
                MunicipalitySubmission,
                Report.submission_id == MunicipalitySubmission.submission_id)\
            .join(Submission,
                  Submission.id == MunicipalitySubmission.submission_id)\
            .filter(MunicipalitySubmission.municipality == self)\
            .filter(Submission.xform_id == submission_subclass.XFORM_ID)\
            .filter(
                and_(Submission.date >= start_date,
                     Submission.date <= end_date))

    def num_trucks_delivered_msw(self, start_date, end_date):
        query = self.get_report_query(
            DailyWaste, start_date, end_date, Report.submission_id)
        return query.count()

    def density_of_msw(self, start_date, end_date):
        query = self.get_report_query(
            DailyWaste, start_date, end_date,
            func.avg(Report.report_json['density'].cast(Float)))
        return query.first()[0]

    def volume_of_msw_processed(self, start_date, end_date):
        query = self.get_report_query(
            DailyWaste, start_date, end_date,
            sqla_sum(Report.report_json['volume'].cast(Float)))
        return query.first()[0]

    def tonnage_of_msw_processed(self, start_date, end_date):
        query = self.get_report_query(
            DailyWaste, start_date, end_date,
            sqla_sum(Report.report_json['tonnage'].cast(Float)))
        return query.first()[0]

    def fuel_consumption(self, start_date, end_date):
        submission_subclass = DailyVehicleDataRegister
        query = (
            DBSession
            .query(sqla_sum(
                submission_subclass.json_data[
                    submission_subclass.FUEL_PURCHASED_LTRS].cast(Float)))
            .join(MunicipalitySubmission,
                  (MunicipalitySubmission.submission_id ==
                   submission_subclass.id))
            .filter(MunicipalitySubmission.municipality == self)
            .filter(submission_subclass.status == Submission.APPROVED)
            .filter(
                and_(Submission.date >= start_date,
                     Submission.date <= end_date)))

        return query.first()[0]

    def vehicle_count(self, start_date, end_date):
        submission_subclass = CompostSalesRegister
        query = MunicipalitySubmission.get_items_query(
            self,
            submission_subclass,
            and_(submission_subclass.status == Submission.APPROVED,
                 submission_subclass.date >= start_date,
                 submission_subclass.date <= end_date))

        return query.count()

    def volume_of_mature_compost(self, start_date, end_date):
        query = self.get_report_query(
            MonthlyRejectsComposition, start_date, end_date,
            sqla_sum(
                Report.report_json['volume_of_mature_compost'].cast(Float)))
        return query.first()[0]

    def average_distance_travelled(self, start_date, end_date):
        submission_subclass = CompostSalesRegister
        query = (
            DBSession
            .query(func.avg(
                submission_subclass.json_data[
                    submission_subclass.DISTANCE_TRAVELLED].cast(Float)))
            .join(MunicipalitySubmission,
                  (MunicipalitySubmission.submission_id ==
                   submission_subclass.id))
            .filter(MunicipalitySubmission.municipality == self)
            .filter(submission_subclass.status == Submission.APPROVED)
            .filter(
                and_(Submission.date >= start_date,
                     Submission.date <= end_date)))

        return query.first()[0]

    def total_windrow_samples(self, start_date, end_date):
        submission_subclass = WindrowMonitoring
        query = MunicipalitySubmission.get_items_query(
            self,
            submission_subclass,
            and_(submission_subclass.status == Submission.APPROVED,
                 submission_subclass.date >= start_date,
                 submission_subclass.date <= end_date))

        return query.count() * WindrowMonitoring.NO_OF_SAMPLE

    def low_windrow_sample_count(self, start_date, end_date):
        query = self.get_report_query(
            WindrowMonitoring, start_date, end_date,
            sqla_sum(
                Report.report_json['low_sample_count'].cast(Integer)))
        return query.first()[0]

    def percentage_of_low_samples(self, start_date, end_date):
        try:
            return (float(self.low_windrow_sample_count(start_date, end_date))
                    / float(self.total_windrow_samples(start_date, end_date)))
        except TypeError:
            return None

    def density_of_mature_compost(self, start_date, end_date):
        query = self.get_report_query(
            MonthlyRejectsComposition, start_date, end_date,
            func.avg(
                Report.report_json['density_of_mature_compost'].cast(Float)))
        return query.first()[0]

    def conversion_factor_mature_to_sieved(self, start_date, end_date):
        query = self.get_report_query(
            MonthlyRejectsComposition, start_date, end_date,
            func.avg(Report.report_json['conversion_factor'].cast(Float)))
        return query.first()[0]

    def quantity_of_compost_produced(self, start_date, end_date):
        query = self.get_report_query(
            MonthlyRejectsComposition, start_date, end_date,
            sqla_sum(
                Report.report_json['quantity_of_compost_produced']
                    .cast(Float)))
        return query.first()[0]

    def quantity_of_compost_sold(self, start_date, end_date):
        query = self.get_report_query(
            CompostSalesRegister, start_date, end_date,
            sqla_sum(
                Report.report_json['weight']
                    .cast(Float)))
        return query.first()[0]

    def volume_of_rejects_from_sieving(self, start_date, end_date):
        query = self.get_report_query(
            DailyRejectsLandfilled, start_date, end_date,
            sqla_sum(
                Report.report_json['volume']
                    .cast(Float)))
        return query.first()[0]

    def electricity_consumption(self, start_date, end_date):
        query = self.get_report_query(
            ElectricityRegister, start_date, end_date,
            sqla_sum(
                Report.report_json['consumption'].cast(Float)))
        return query.first()[0]

    def leachete_volume_accumulated(self, start_date, end_date):
        query = self.get_report_query(
            LeacheteMonthlyRegister, start_date, end_date,
            sqla_sum(
                Report.report_json['volume'].cast(Float)))
        return query.first()[0]

    def density_of_rejects_from_sieving(self, start_date, end_date):
        query = self.get_report_query(
            MonthlyRejectsDensity, start_date, end_date,
            func.avg(
                Report.report_json['density']
                    .cast(Float)))
        return query.first()[0]

    def quantity_of_rejects_from_sieving_landfilled(
            self, start_date, end_date):
        query = self.get_report_query(
            DailyRejectsLandfilled, start_date, end_date,
            sqla_sum(
                Report.report_json['tonnage']
                    .cast(Float)))
        return query.first()[0]

    def url(self, request, action=None):
        traverse = (self.id, action) if action else (self.id,)
        return request.route_url(
            'municipalities', traverse=traverse)

    def get_skip(self, skip_type):
        """
        Get the Skip with the specified skip_type that is tied to this
        municipality

        Meant to be used form within views where we can handle a None result
        gracefully. Also caches the skip by type for subsequent queries

        :param skip_type: Skip type, ideally between [A-Z]
        :return: The skip or None
        """
        if skip_type in self._skips:
            return self._skips[skip_type]
        else:
            try:
                skip = Skip.get(Skip.municipality == self,
                                Skip.skip_type == skip_type)
            except NoResultFound:
                self._skips[skip_type] = None
            else:
                self._skips[skip_type] = skip
            return self._skips[skip_type]


class MunicipalityFactory(ModelFactory):
    __acl__ = [
        (Allow, security.MUNICIPALITY_MANAGE_ALL.key, 'manage')
    ]

    def __getitem__(self, item):
        try:
            municipality_id = int(item)
            record = Municipality.get(Municipality.id == municipality_id)
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            record.__name__ = item
            record.__parent__ = self
            record.request = self.request
            return record

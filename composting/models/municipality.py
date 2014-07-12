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
from composting.models.user import User
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

    def report(self, start_date, end_date):
        """
        Return row and headers for the municipality report
        """
        headers = []
        rows = []
        headers = ["", "Parameter", "Unit", "Value", "Comments"]

        # MWS reports
        volume_of_msw_processed = self.volume_of_msw_processed(
            start_date, end_date) or 0
        rows.append(
            ["MWS", "Volume of MSW processed", "m3", volume_of_msw_processed,
             "Consistency with normal monthly supply"])

        density_of_msw = self.density_of_msw(start_date, end_date) or 0
        rows.append(
            ["", "Density of MSW", "t/m3", density_of_msw,
             "Consistency with normal monthly supply"])

        tonnage_of_msw_processed = self.tonnage_of_msw_processed(
            start_date, end_date) or 0
        rows.append(
            ["", "Quantity of MSW processed", "Tonnes",
             tonnage_of_msw_processed, ""])

        num_trucks_delivered_msw = self.num_trucks_delivered_msw(
            start_date, end_date) or 0
        rows.append(
            ["", "Number of trucks having delivered MSW", "Tonnes",
             num_trucks_delivered_msw, "Consistency with normal activity"])

        # Compost reports
        volume_of_mature_compost = self.volume_of_mature_compost(
            start_date, end_date) or "-"
        rows.append(
            ["Compost", "Volume of mature compost (Qmc)", "m3",
             volume_of_mature_compost, ""])

        density_of_mature_compost = self.density_of_mature_compost(
            start_date, end_date) or "-"
        rows.append(
            ["", "Density of mature compost (Dmc)", "Ton/m3",
             density_of_mature_compost, "Consistency with previous months"])

        conversion_factor_mature_to_sieved = (
            self.conversion_factor_mature_to_sieved(start_date, end_date) or
            "-")
        rows.append(
            ["", "Conversion factor mature to sieved (WSieved/WMature)",
             "N/A", conversion_factor_mature_to_sieved,
             "Comparison with Quantity of rejects from sieving"])

        quantity_of_compost_produced = (
            self.quantity_of_compost_produced(start_date, end_date) or "-")
        rows.append(
            ["", "Quantity of compost produced (Qpc)", "Tonnes",
             quantity_of_compost_produced,
             "Consistency with normal monthly production"])

        quantity_of_compost_sold = (
            self.quantity_of_compost_sold(start_date, end_date) or "-")
        rows.append(
            ["", "Quantity of compost sold", "Tonnes",
             quantity_of_compost_sold,
             "Consistency with compost produced"])

        vehicle_count = self.vehicle_count(start_date, end_date) or 0
        rows.append(
            ["", "Number of vehicles having transported compost", "N/A",
             vehicle_count, "Comparison with previous months"])

        average_distance = (
            self.average_distance_travelled(start_date, end_date) or "-")
        rows.append(
            ["", "Average distance travelled by vehicles transporting compost",
             "Kms", average_distance, "Comparison with previous months"])

        volume_of_rejects_from_sieving = (
            self.volume_of_rejects_from_sieving(start_date, end_date) or "-")
        rows.append(
            ["Rejects from sieving",
             "Volume of rejects from sieving landfilled",
             "Tonnes", volume_of_rejects_from_sieving, ""])

        density_of_rejects_from_sieving = (
            self.density_of_rejects_from_sieving(start_date, end_date))
        rows.append(
            ["",
             "Density of rejects from sieving",
             "Ton/m3", density_of_rejects_from_sieving or "-", ""])

        quantity_of_rejects_from_sieving_landfilled = (
            self.quantity_of_rejects_from_sieving_landfilled(start_date,
                                                             end_date))
        rows.append(
            ["",
             "Quantity of rejects from sieving landfilled",
             "Tonnes", quantity_of_rejects_from_sieving_landfilled or "-",
             "Consistency with previous months"])

        if (quantity_of_rejects_from_sieving_landfilled and
                quantity_of_compost_sold):
            reject_ratio = (
                quantity_of_rejects_from_sieving_landfilled /
                quantity_of_compost_sold)
        else:
            reject_ratio = "-"

        rows.append(
            ["", "", "%", reject_ratio, "Consistency with previous months"])

        total_windrow_samples = (
            self.total_windrow_samples(start_date, end_date))
        rows.append(
            ["Oxygen content",
             "Total # of samples",
             "N/A", total_windrow_samples or 0,
             "Normal operation (about 240 samples for 4 windrows)"])

        low_windrow_sample_count = (
            self.low_windrow_sample_count(start_date, end_date))
        rows.append(
            ["",
             "Total # of samples below 10%",
             "N/A", low_windrow_sample_count or "-",
             "Normal operation (about 240 samples for 4 windrows)"])

        if total_windrow_samples and low_windrow_sample_count:
            percentage_of_low_samples = (
                low_windrow_sample_count / total_windrow_samples)
        else:
            percentage_of_low_samples = "-"

        rows.append(
            ["", "", "%", percentage_of_low_samples,
             "Normal operation (about 240 samples for 4 windrows)"])

        fuel_consumption = self.fuel_consumption(start_date, end_date) or "-"
        rows.append(
            ["Energy",
             "Fuel consumption (on site)", "Litres", fuel_consumption,
             "Consistency with MSW processed"])

        electricity_consumption = (
            self.electricity_consumption(start_date, end_date) or "-")
        rows.append(
            ["", "Electricity consumption", "MWh", electricity_consumption,
             "Consistency with normal activity"])

        leachete_volume_accumulated = (
            self.leachete_volume_accumulated(start_date, end_date) or "-")
        rows.append(
            ["Leachate", "Volume of leachate accumulated in 24 hours", "m3",
             leachete_volume_accumulated, "Any impacting factors"])

        return headers, rows

    def get_users_by_group_query(self, group):
        return DBSession.query(User)\
            .filter(User.group == group,
                    User.municipality == self)

    @property
    def site_managers(self):
        """
        Get the list of users who are the site managers for this municipality
        :return: list
        """
        return self.get_users_by_group_query(security.SITE_MANAGER.key).all()

    @property
    def data_entry_clerks(self):
        """
        Get the list of users who are the site managers for this municipality
        :return: list
        """
        return self.get_users_by_group_query(
            security.DATA_ENTRY_CLERK.key).all()


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

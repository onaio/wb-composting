from sqlalchemy.orm.exc import NoResultFound
from dashboard.constants import XFORM_ID_STRING
from dashboard.libs import SubmissionHandler

from composting import constants
from composting.models.base import DBSession
from composting.models.user import User
from composting.models.municipality import Municipality
from composting.models.monthly_density import MonthlyDensity
from composting.models.monthly_waste_composition import MonthlyWasteComposition
from composting.models.daily_waste import DailyWaste
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.windrow_monitoring import WindrowMonitoring
from composting.models.daily_rejects_landfilled import DailyRejectsLandfilled
from composting.models.monthly_rejects_density import MonthlyRejectsDensity
from composting.models.electricity_register import ElectricityRegister
from composting.models.leachete_monthly_register import LeacheteMonthlyRegister
from composting.models.compost_sales_register import CompostSalesRegister
from composting.models.compost_density_register import CompostDensityRegister
from composting.models.monthly_rejects_composition import (
    MonthlyRejectsComposition)
from composting.models.daily_vehicle_register import DailyVehicleDataRegister
from composting.models.submission import Submission


class MunicipalitySubmissionHandler(SubmissionHandler):
    # mapping of id strings to classes
    XFORM_CLASS_MAPPING = {
        MonthlyDensity.XFORM_ID: MonthlyDensity,
        DailyWaste.XFORM_ID: DailyWaste,
        constants.MONTHLY_WASTE_COMPOSITION_FORM: MonthlyWasteComposition,
        WindrowMonitoring.XFORM_ID: WindrowMonitoring,
        DailyRejectsLandfilled.XFORM_ID: DailyRejectsLandfilled,
        MonthlyRejectsDensity.XFORM_ID: MonthlyRejectsDensity,
        ElectricityRegister.XFORM_ID: ElectricityRegister,
        LeacheteMonthlyRegister.XFORM_ID: LeacheteMonthlyRegister,
        CompostSalesRegister.XFORM_ID: CompostSalesRegister,
        CompostDensityRegister.XFORM_ID: CompostDensityRegister,
        MonthlyRejectsComposition.XFORM_ID: MonthlyRejectsComposition,
        DailyVehicleDataRegister.XFORM_ID: DailyVehicleDataRegister
    }

    @staticmethod
    def can_handle(json_payload):
        return json_payload[XFORM_ID_STRING] in [
            MonthlyDensity.XFORM_ID,
            DailyWaste.XFORM_ID,
            constants.MONTHLY_WASTE_COMPOSITION_FORM,
            DailyRejectsLandfilled.XFORM_ID,
            MonthlyRejectsDensity.XFORM_ID,
            ElectricityRegister.XFORM_ID,
            LeacheteMonthlyRegister.XFORM_ID,
            CompostSalesRegister.XFORM_ID,
            CompostDensityRegister.XFORM_ID,
            MonthlyRejectsComposition.XFORM_ID,
            DailyVehicleDataRegister.XFORM_ID
        ]

    @classmethod
    def create_submission(cls, json_payload, **kwargs):
        xform_id = json_payload[XFORM_ID_STRING]
        # get the specific submission sub-class
        try:
            klass = MunicipalitySubmissionHandler.XFORM_CLASS_MAPPING[xform_id]
        except KeyError:
            raise ValueError("No xform class mapping to '{}'".format(xform_id))
        else:
            # determine the date the data is in reference of
            date = klass.datetime_from_json(
                json_payload, klass.DATE_FIELD, klass.DATE_FORMAT).date()
            return klass(
                xform_id=json_payload[XFORM_ID_STRING],
                json_data=json_payload,
                date=date,
                **kwargs)

    @classmethod
    def get_or_create_submission(cls, json_payload, **kwargs):
        ona_sub_id = json_payload[constants.ONA_SUBMISSION_ID]
        try:
            submission = (
                Submission.get(
                    Submission.json_data[constants.ONA_SUBMISSION_ID].astext ==
                    str(ona_sub_id)))
            # Submission already exists so update its json_payload
            submission.json_data = json_payload
            return submission, True
        except NoResultFound:
            submission = cls.create_submission(json_payload, **kwargs)

            # Submission does not exist
            return submission, False

    @classmethod
    def get_municipality_from_payload(cls, json_payload):
        """
        Try to determine the municipality the submission user belongs to from
        the payload
        :return: Municipality or None
        """
        submitted_by = json_payload.get(constants.SUBMITTED_BY)
        if submitted_by is None:
            return None

        # find the user and join to municipality
        try:
            municipality = DBSession.query(Municipality)\
                                    .select_from(User)\
                                    .filter(User.username == submitted_by)\
                                    .join(Municipality).one()
        except NoResultFound:
            return None
        else:
            return municipality

    def __call__(self, json_payload, **kwargs):
        submission, is_updated = self.get_or_create_submission(
            json_payload, **kwargs)

        if not is_updated:
            # determine the municipality id(object)
            municipality = self.get_municipality_from_payload(json_payload)

            if municipality is not None:
                municipality_submission = MunicipalitySubmission(
                    submission=submission,
                    municipality=municipality)

                DBSession.add(municipality_submission)
                return

        # add the submission because we can save even when we can't determine
        # its municipality
        DBSession.add(submission)

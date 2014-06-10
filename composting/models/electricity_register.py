from zope.interface import implementer
from sqlalchemy import desc

from composting.models.base import DBSession
from composting.models.submission import Submission, ISubmission
from composting.models.municipality_submission import MunicipalitySubmission
from composting.libs.utils import get_previous_month_year, get_month_start_end


@implementer(ISubmission)
class ElectricityRegister(Submission):
    XFORM_ID = 'municipality_electricity_register'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'month_year'
    DATE_FORMAT = '%Y-%m-%d'
    METER_READING_FIELD = 'meter_reading'

    LIST_ACTION_NAME = 'municipality-electricity-register'

    @classmethod
    def get_last_meter_reading(cls, municipality, current_date):
        """
        Based on the specified month/year, get the meter reading for said
        municipality for the previous month, or None

        :param municipality: Municipality to check
        :param current_date: The current month/year with day set to 01
        :return: the ElectricityRegister record or None
        """
        # get the start end dates for the current month
        start, end = get_month_start_end(current_date)
        # determine the previous month/year
        previous_month_year = get_previous_month_year(current_date)

        # select the `newest` ElectricityRegister->meter_reading that falls
        # under previous_month_year
        result = DBSession.query(
            cls.json_data[cls.METER_READING_FIELD].astext)\
            .select_from(MunicipalitySubmission)\
            .join(MunicipalitySubmission.submission)\
            .filter(MunicipalitySubmission.municipality == municipality,
                    Submission.date >= previous_month_year,
                    Submission.date < start)\
            .order_by(desc(Submission.date))\
            .limit(1)\
            .first()
        return result and result[0] or None

    def consumption_since_last_reading(self, municipality):
        last_reading = self.get_last_meter_reading(municipality, self.date)
        if last_reading is None:
            return None

        last_reading = float(last_reading)
        current_reading = float(self.json_data[self.METER_READING_FIELD])
        return current_reading - last_reading
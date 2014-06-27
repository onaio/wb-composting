from zope.interface import implementer
from sqlalchemy import desc

from composting.libs.utils import get_month_start_end
from composting.models.base import DBSession
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class CompostDensityRegister(Submission):
    XFORM_ID = 'monthly_compost_density_register'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'month_year'
    DATE_FORMAT = '%Y-%m-%d'
    FILLED_BOX_WEIGHT_FIELD = 'filled_box_weight'
    EMPTY_BOX_WEIGHT_FIELD = 'empty_box_weight'

    LIST_ACTION_NAME = 'monthly-compost-density-register'

    @property
    def net_weight(self):
        return float(self.json_data[self.FILLED_BOX_WEIGHT_FIELD])\
            - float(self.json_data[self.EMPTY_BOX_WEIGHT_FIELD])

    def density(self, municipality):
        return self.net_weight / municipality.box_volume

    @classmethod
    def get_by_date(cls, date, municipality, *criterion):
        from composting.models.municipality_submission import\
            MunicipalitySubmission
        """
        Tries to retrieve newest compost density record for whichever month is
        specified by date
        :param date: the target month
        :return:
        """
        start, end = get_month_start_end(date)
        return DBSession.query(cls)\
            .select_from(MunicipalitySubmission)\
            .join(cls)\
            .filter(
                    cls.xform_id == cls.XFORM_ID,
                    cls.date >=start,
                    cls.date <= end,
                    MunicipalitySubmission.municipality == municipality,
                    *criterion)\
            .order_by(desc(cls.date))\
            .first()
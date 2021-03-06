from zope.interface import implementer
from sqlalchemy import desc

from composting.constants import KGS_PER_TONNE
from composting.libs.utils import get_month_start_end
from composting.models.base import DBSession
from composting.models.compost_density_register import CompostDensityRegister
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class CompostSalesRegister(Submission):
    XFORM_ID = 'compost_sales_register'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'date'
    DATE_FORMAT = '%Y-%m-%d'
    IS_BAGGED_COMPOST_FIELD = 'bagged_compost'
    COMPOST_LENGTH_FIELD = 'compost_length'
    COMPOST_WIDTH_FIELD = 'compost_width'
    COMPOST_HEIGHT_FIELD = 'compost_height'
    BAGGED_COMPOST_WEIGHT_FIELD = 'bagged_compost_weight'
    DISTANCE_TRAVELLED = 'supply_distance'

    LIST_ACTION_NAME = 'outgoing-compost-sales-register'
    FORM_ID = "2390"

    _compost_density = None
    _density = None

    @property
    def volume(self):
        if self.json_data[self.IS_BAGGED_COMPOST_FIELD] == 'yes':
            return None

        return float(self.json_data[self.COMPOST_LENGTH_FIELD])\
            * float(self.json_data[self.COMPOST_WIDTH_FIELD])\
            * float(self.json_data[self.COMPOST_HEIGHT_FIELD])

    def get_compost_density(self, municipality):
        start, end = get_month_start_end(self.date)
        # with our date as ref. find the density for the month
        self._compost_density = self._compost_density\
            or DBSession.query(CompostDensityRegister)\
            .select_from(MunicipalitySubmission)\
            .join(MunicipalitySubmission.submission)\
            .filter(MunicipalitySubmission.municipality == municipality,
                    CompostDensityRegister.date >= start,
                    CompostDensityRegister.date <= end,
                    CompostDensityRegister.status == Submission.APPROVED)\
            .order_by(desc(CompostDensityRegister.date))\
            .limit(1)\
            .first()
        return self._compost_density

    def density(self):
        if self.municipality_submission is None:
            return None
        municipality = self.municipality_submission.municipality

        compost_density = self.get_compost_density(municipality)
        if compost_density is None:
            return None

        self._density = self._density or compost_density.density()
        return self._density

    def weight(self):
        # if compost was bagged, return weight directly
        if self.json_data[self.IS_BAGGED_COMPOST_FIELD] == 'yes':
            return float(self.json_data[self.BAGGED_COMPOST_WEIGHT_FIELD])

        volume = self.volume
        density = self.density()
        if volume is None or density is None:
            return None

        return (density * volume) / KGS_PER_TONNE

    def create_or_update_report(self):
        report = self.get_or_create_report()
        weight = self.weight()
        if weight is None:
            raise ValueError("Cannot create a report if the weight is invalid")
        report.report_json = {
            'weight': weight
        }
        return report

    def can_approve(self, request):
        return super(CompostSalesRegister, self).can_approve(request)\
            and self.density() is not None

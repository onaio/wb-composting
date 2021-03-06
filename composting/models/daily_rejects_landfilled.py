from zope.interface import implementer
from sqlalchemy import desc

from composting.constants import KGS_PER_TONNE
from composting.libs.utils import get_month_start_end
from composting.models.base import DBSession
from composting.models.submission import Submission, ISubmission
from composting.models.municipality import MunicipalitySubmission
from composting.models.monthly_rejects_density import MonthlyRejectsDensity


@implementer(ISubmission)
class DailyRejectsLandfilled(Submission):
    XFORM_ID = 'register_daily_rejects_landfilled'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'date'
    DATE_FORMAT = '%Y-%m-%d'
    BARROWS_FROM_SIEVING_FIELD = 'barrows_number_frm_sieving'
    FORM_ID = "2321"

    LIST_ACTION_NAME = 'daily-rejects-landfilled'

    def get_monthly_rejects_density(self):
        """
        Get the monthly density of rejects from sieving instance which matches
        this date and is approved
        :return: MonthlyRejectsDensity monthly rejects density record or None
        if not found
        """
        municipality_submission = self.municipality_submission
        if municipality_submission is None:
            return None

        start, end = get_month_start_end(self.date)
        return DBSession\
            .query(MonthlyRejectsDensity)\
            .select_from(MunicipalitySubmission)\
            .join(MonthlyRejectsDensity)\
            .filter(
                MunicipalitySubmission.municipality
                == municipality_submission.municipality,
                MonthlyRejectsDensity.xform_id
                == MonthlyRejectsDensity.XFORM_ID,
                MonthlyRejectsDensity.date >= start,
                MonthlyRejectsDensity.date <= end,
                MonthlyRejectsDensity.status == Submission.APPROVED)\
            .order_by(desc(MonthlyRejectsDensity.date))\
            .first()

    def volume(self):
        if hasattr(self, '_volume'):
            return self._volume

        municipality_submission = self.municipality_submission
        if municipality_submission is None:
            self._volume = None
            return self._volume

        density = self.get_monthly_rejects_density()
        if density is None:
            self._volume = None
            return self._volume

        self._volume = (municipality_submission.municipality.wheelbarrow_volume
                        * int(self.json_data[self.BARROWS_FROM_SIEVING_FIELD]))
        return self._volume

    def can_approve(self, request):
        return super(DailyRejectsLandfilled, self).can_approve(request)\
            and self.volume() is not None

    def create_or_update_report(self):
        report = self.get_or_create_report()
        volume = self.volume()
        if volume is None:
            raise ValueError(
                "The volume cannot be None when creating the report")
        monthly_rejects_density = self.get_monthly_rejects_density()
        if monthly_rejects_density is None:
            raise ValueError(
                "The monthly_rejects_density cannot be None when creating the"
                " report")
        municipality = self.municipality_submission.municipality
        density = monthly_rejects_density.density(municipality) / KGS_PER_TONNE
        tonnage = volume * density
        report.report_json = {
            'volume': volume,
            'tonnage': tonnage
        }
        report.save()
        return report

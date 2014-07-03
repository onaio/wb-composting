import transaction
from datetime import date

from composting.models.base import DBSession
from composting.models.submission import Submission
from composting.models.municipality import Municipality
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.monthly_rejects_density import MonthlyRejectsDensity
from composting.models.daily_rejects_landfilled import DailyRejectsLandfilled
from composting.tests.test_base import TestBase


class TestDailyRejectsLandfilled(TestBase):
    def test_get_monthly_rejects_density_returns_none_if_no_municipality(self):
        rejects_landfilled = DailyRejectsLandfilled()
        self.assertIsNone(rejects_landfilled.get_monthly_rejects_density())

    def test_get_monthly_rejects__density_returns_none_if_no_result(self):
        self.setup_test_data()
        municipality = Municipality.get(Municipality.name == "Mukono")
        rejects_landfilled = DailyRejectsLandfilled(
            date=date(2012, 1, 1),
            municipality_submission=MunicipalitySubmission(
                municipality=municipality
            )
        )
        self.assertIsNone(rejects_landfilled.get_monthly_rejects_density())

    def test_get_monthly_rejects_density_returns_none_if_exists(self):
        self.setup_test_data()
        with transaction.manager:
            DBSession.query(MonthlyRejectsDensity).update({
                'status': Submission.APPROVED
            })
        municipality = Municipality.get(Municipality.name == "Mukono")
        rejects_landfilled = DailyRejectsLandfilled(
            date=date(2014, 6, 13),
            municipality_submission=MunicipalitySubmission(
                municipality=municipality
            )
        )
        monthly_rejects_landfilled = rejects_landfilled\
            .get_monthly_rejects_density()
        self.assertIsInstance(monthly_rejects_landfilled,
                              MonthlyRejectsDensity)

    def test_volume_calculation(self):
        self.setup_test_data()
        with transaction.manager:
            DBSession.query(MonthlyRejectsDensity).update({
                'status': Submission.APPROVED
            })
        municipality = Municipality.get(Municipality.name == "Mukono")
        rejects_landfilled = DailyRejectsLandfilled(
            date=date(2014, 6, 13),
            json_data={
                'barrows_number_frm_sieving': '10'
            },
            municipality_submission=MunicipalitySubmission(
                municipality=municipality
            )
        )
        self.assertEqual(rejects_landfilled.volume(), 6.25)

    def test_create_or_update_report(self):
        self.setup_test_data()
        with transaction.manager:
            DBSession.query(MonthlyRejectsDensity).update({
                'status': Submission.APPROVED
            })
        municipality = Municipality.get(Municipality.name == "Mukono")
        rejects_landfilled = DailyRejectsLandfilled(
            date=date(2014, 6, 13),
            json_data={
                'barrows_number_frm_sieving': '10'
            },
            municipality_submission=MunicipalitySubmission(
                municipality=municipality
            )
        )
        report = rejects_landfilled.create_or_update_report()
        self.assertEqual(report.report_json, {
            'volume': 6.25,
            'tonnage': 1.7999999999999998
        })
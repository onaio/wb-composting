from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound

from dashboard.views.base import BaseView

from composting.models import DailyWaste, Submission


@view_defaults(route_name='daily-waste', context=DailyWaste)
class DailyWastes(BaseView):
    @view_config(name='', renderer='default.jinja2')
    def show(self):
        return {}

    @view_config(name='approve', request_method='POST')
    def approve(self):
        daily_waste = self.request.context
        daily_waste.submission.status = Submission.APPROVED
        daily_waste.save()

        # todo: use daily_waste.municipality.id in redirect
        return HTTPFound(
            self.request.route_url(
                'municipalities', traverse=('1', 'daily-waste')))

    @view_config(name='reject', request_method='POST')
    def reject(self):
        daily_waste = self.request.context
        daily_waste.submission.status = Submission.REJECTED
        daily_waste.save()

        # todo: use daily_waste.municipality.id in redirect
        return HTTPFound(
            self.request.route_url(
                'municipalities', traverse=('1', 'daily-waste')))

    @view_config(name='unapprove', request_method='POST')
    def unapprove(self):
        daily_waste = self.request.context
        daily_waste.submission.status = Submission.PENDING
        daily_waste.save()

        # todo: use daily_waste.municipality.id in redirect
        return HTTPFound(
            self.request.route_url(
                'municipalities', traverse=('1', 'daily-waste')))
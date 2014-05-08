from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound

from dashboard.views.base import BaseView

from composting.models import DailyWaste


@view_defaults(route_name='daily-waste', context=DailyWaste)
class DailyWastes(BaseView):
    @view_config(name='', renderer='default.jinja2')
    def show(self):
        return {}

    @view_config(name='approve', request_method='POST')
    def approve(self):
        daily_waste = self.request.context
        # todo: use daily_waste.municipality.id in redirect
        return HTTPFound(
            self.request.route_url(
                'municipalities', traverse=('1', 'daily-waste')))
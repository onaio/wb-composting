from pyramid.view import view_defaults, view_config

from dashboard.views.base import BaseView

from composting.models import Municipality


@view_defaults(route_name='municipalities', context=Municipality)
class Municipalities(BaseView):
    @view_config(name='', renderer='overview.jinja2')
    def index(self):
        municipality = self.request.context
        return {
            'municipality': municipality
        }

    @view_config(name='daily-waste', renderer='daily_waste.jinja2')
    def daily_waste(self):
        municipality = self.request.context
        return {
            'municipality': municipality
        }

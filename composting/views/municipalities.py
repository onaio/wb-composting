from pyramid.view import view_defaults, view_config

from dashboard.views.base import BaseView

from composting.views.helpers import selections_from_request
from composting.models import Municipality, DailyWaste, Submission



@view_defaults(route_name='municipalities', context=Municipality)
class Municipalities(BaseView):
    @view_config(name='', renderer='overview.jinja2')
    def index(self):
        municipality = self.request.context
        return {
            'municipality': municipality
        }

    @view_config(name='daily-waste', renderer='daily_waste.jinja2')
    def daily_waste_list(self):
        municipality = self.request.context
        statuses = [Submission.PENDING, Submission.APPROVED,
                    Submission.REJECTED]
        status_selections = selections_from_request(
            self.request,
            statuses,
            lambda status: status == '1',
            [Submission.PENDING, Submission.REJECTED])

        criterion = Submission.status.in_(status_selections)
        daily_wastes = municipality.get_register_records(DailyWaste, criterion)

        status = dict([(s, s in statuses) for s in status_selections])
        from datetime import date
        return {
            'municipality': municipality,
            'daily_wastes': daily_wastes,
            'status': status
        }
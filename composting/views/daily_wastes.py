from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from dashboard.views.base import BaseView

from composting.models import DailyWaste, Submission


@view_defaults(route_name='daily-waste', context=DailyWaste)
class DailyWastes(BaseView):
    @view_config(name='', renderer='default.jinja2')
    def show(self):
        return {}

    @view_config(
        name='approve', request_method='POST',
        wrapper='update_status_wrapper')
    def approve(self):
        self.request.new_status = Submission.APPROVED
        self.request.action = 'daily-waste'
        return Response(None)

    @view_config(name='reject', request_method='POST',
                 wrapper='update_status_wrapper')
    def reject(self):
        self.request.new_status = Submission.REJECTED
        self.request.action = 'daily-waste'
        return Response(None)

    @view_config(name='unapprove', request_method='POST',
                 wrapper='update_status_wrapper')
    def unapprove(self):
        self.request.new_status = Submission.PENDING
        self.request.action = 'daily-waste'
        return Response(None)
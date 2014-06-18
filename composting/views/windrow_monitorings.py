from pyramid.view import view_defaults, view_config
from dashboard.views.base import BaseView

from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.windrow_monitoring import (
    WindrowMonitoring, WindrowMonitoringFactory)


@view_defaults(route_name='municipalities', permission='show')
class WindrowMonitorings(BaseView):
    @view_config(
        name='',
        context=WindrowMonitoringFactory,
        renderer='windrow_monitoring_list_by_no.jinja2')
    def list_by_windrow_no(self):
        municipality = self.request.context.__parent__
        windrow_no = '/'.join(self.request.subpath)
        criterion = WindrowMonitoring.windrow_no == windrow_no
        municipality_submissions = MunicipalitySubmission.get_items(
            municipality, WindrowMonitoring, criterion)

        windrow_records = [s for m, s in municipality_submissions]
        return {
            'municipality': municipality,
            'windrow_records': windrow_records,
            'windrow_no': windrow_no
        }
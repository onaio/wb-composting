from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults, view_config
from deform import Form, ValidationFailure, Button

from dashboard.views.base import BaseView

from composting.views.helpers import selections_from_request
from composting.models import Municipality, DailyWaste, Submission, Skip
from composting.forms import SkipForm



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
        return {
            'municipality': municipality,
            'daily_wastes': daily_wastes,
            'status': status
        }

    @view_config(name='skips', renderer='skips.jinja2')
    def skips(self):
        municipality = self.request.context
        skips = municipality.get_skips()
        return {
            'skips': skips,
            'municipality': municipality,
        }

    @view_config(name='create-skip', renderer='create_skip.jinja2')
    def create_skip(self):
        municipality = self.request.context
        form = Form(
            SkipForm().bind(
                request=self.request,
                municipality_id=municipality.id),
            buttons=('Save', Button(name='cancel', type='button')))
        if self.request.method == "POST":
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                self.request.session.flash(
                    u"Please fix the errors indicated below.", "error")
            else:
                skip = Skip(municipality=municipality, **values)
                skip.save()
                self.request.session.flash(
                    u"Your changes have been saved.", "success")
                return HTTPFound(
                    self.request.route_url(
                        'skips', traverse=(skip.id, 'edit')))
        return {
            'municipality': municipality,
            'form': form
        }
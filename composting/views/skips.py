from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults, view_config
from deform import Form, ValidationFailure, Button

from dashboard.views.base import BaseView

from composting.models.base import DBSession
from composting.models import Skip
from composting.forms import SkipForm



@view_defaults(route_name='skips', context=Skip)
class Skips(BaseView):
    @view_config(name='edit', renderer='edit_skip.jinja2')
    def edit(self):
        skip = self.request.context
        municipality = skip.municipality
        form = Form(
            SkipForm().bind(
                request=self.request,
                municipality_id=municipality.id,
                skip_id=skip.id),
            buttons=('Save', Button(name='cancel', type='button')),
            appstruct=skip.appstruct)
        if self.request.method == "POST":
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                self.request.session.flash(
                    u"Please fix the errors indicated below.", "error")
            else:
                skip.__dict__.update(**values)
                skip.save()
                self.request.session.flash(
                    u"Your changes have been saved.", "success")
                return HTTPFound(
                    self.request.route_url(
                        'skips', traverse=(skip.id, 'edit')))
        return {
            'skip': skip,
            'municipality': municipality,
            'form': form
        }

    @view_config(name='delete', request_method='POST')
    def delete(self):
        skip = self.request.context
        municipality_id = skip.municipality_id
        DBSession.delete(skip)
        return HTTPFound(
            self.request.route_url(
                'municipalities', traverse=(municipality_id, 'skips')))
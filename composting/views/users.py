from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from deform import Form, ValidationFailure, Button
from dashboard.views.base import BaseView

from composting.forms.user_form import UserForm
from composting.models.user import User, UserFactory


@view_defaults(route_name='users', context=User, permission='manage')
class Users(BaseView):
    @view_config(context=UserFactory, renderer='admin_users_list.jinja2')
    def list(self):
        users = User.all()
        return {
            'users': users
        }

    @view_config(name='toggle-status', request_method='POST', check_csrf=True)
    def toggle_status(self):
        user = self.request.context

        # users cannot make themselves in-active
        if self.request.user == user and user.active is True:
            self.request.session.flash(
                "You cannot de-activate your own account", 'error')
        else:
            user.active = not user.active
            user.save()
            self.request.session.flash(
                "Your changes have been saved", 'success')

        return HTTPFound(self.request.route_url('users', traverse=()))

    @view_config(name='edit', renderer='admin_users_edit.jinja2')
    def edit(self):
        user = self.request.context
        form = Form(
            UserForm().bind(
                request=self.request,
                user=user),
            buttons=('Save', Button(name='cancel', type='button')),
            appstruct=user.appstruct)
        if self.request.method == 'POST':
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                pass
            else:
                user.update(values['group'], values['municipality_id'])
                self.request.session.flash(
                    "Your changes have been saved", 'success')
                return HTTPFound(
                    self.request.route_url(
                        'users', traverse=(user.id, 'edit')))
        return {
            'form': form
        }
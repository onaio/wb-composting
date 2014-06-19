from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound

from dashboard.views.base import BaseView
from composting.models.user import User, UserFactory


@view_defaults(route_name='users', context=User)
class Users(BaseView):
    @view_config(context=UserFactory, renderer='admin_users_list.jinja2')
    def list(self):
        users = User.all()
        return {
            'users': users
        }

    @view_config(name='toggle-status', request_method='POST')
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
from pyramid.view import view_defaults, view_config

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
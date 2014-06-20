from pyramid.security import (
    NO_PERMISSION_REQUIRED, remember, forget)
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pyramid.response import Response
from pyramid.view import (
    view_config,
    forbidden_view_config,
    render_view
)
from sqlalchemy.orm.exc import NoResultFound
from dashboard.views.helpers import check_post_csrf

from composting.models.user import User


@forbidden_view_config()
def forbidden(context, request):
    # if not authenticated, show login screen with unauthorized status code
    if not request.user:
        return Response(
            render_view(
                context, request, 'sign_in', secure=False), status=401)
    # otherwise, raise HTTPForbidden
    return HTTPForbidden()


@view_config(route_name='auth',
             match_param='action=sign-in',
             permission=NO_PERMISSION_REQUIRED,
             renderer='sign_in.jinja2',
             decorator=check_post_csrf)
@view_config(name='sign_in',
             context=HTTPForbidden,
             permission=NO_PERMISSION_REQUIRED,
             renderer='sign_in.jinja2',
             decorator=check_post_csrf)
def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.get(User.username == username)
        except NoResultFound:
            # we're still here set the error message
            request.session.flash(u"Invalid username or password", 'error')
        else:
            if user.active is False:
                # we're still here set the error message
                request.session.flash(
                    u"Inactive account, please contact your supervisor",
                    'error')
            elif user.check_password(password):
                headers = remember(request, user.id)
                return HTTPFound(
                    request.route_url(
                        'municipalities', traverse=()), headers=headers)
            else:
                # we're still here set the error message
                request.session.flash(u"Invalid username or password", 'error')
    return {}


@view_config(route_name='auth', match_param='action=sign-out')
def sign_out(request):
    headers = forget(request)
    return HTTPFound(
        request.route_url(
            'auth', action='sign-in'), headers=headers)
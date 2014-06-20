import json

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
from requests_oauthlib import OAuth2Session

from composting.models.user import User


@forbidden_view_config()
def forbidden(context, request):
    # if not authenticated, show login screen with unauthorized status code
    if not request.user:
        return Response(
            render_view(
                context, request, 'oauth_login', secure=False), status=401)
    # otherwise, raise HTTPForbidden
    return HTTPForbidden()


@view_config(route_name='oauth',
             match_param='action=sign-in',
             permission=NO_PERMISSION_REQUIRED,
             renderer='oauth_sign_in.jinja2',
             decorator=check_post_csrf)
@view_config(name='oauth_login',
             context=HTTPForbidden,
             permission=NO_PERMISSION_REQUIRED,
             renderer='oauth_sign_in.jinja2',
             decorator=check_post_csrf)
def oauth_login(request):
    return {}


@view_config(route_name='auth',
             match_param='action=sign-in',
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
            'municipalities', traverse=()), headers=headers)


@view_config(route_name='oauth',
             match_param='action=authorize',
             permission=NO_PERMISSION_REQUIRED,)
def oauth_authorize(request):
    client_id = request.registry.settings['oauth_client_id']
    authorization_endpoint = "{base_url}{path}".format(
        base_url=request.registry.settings['oauth_base_url'],
        path=request.registry.settings['oauth_authorization_path'])
    redirect_uri = request.route_url('oauth', action='callback')

    session = OAuth2Session(
        client_id,
        scope=['read', 'groups'],
        redirect_uri=redirect_uri)
    authorization_url, state = session.authorization_url(
        authorization_endpoint)
    # State is used to prevent CSRF, keep this for later.
    request.session['oauth_state'] = state
    return HTTPFound(authorization_url)


@view_config(
    route_name='oauth',
    match_param='action=callback',
    permission=NO_PERMISSION_REQUIRED)
def oauth_callback(request):
    # check if we have `error` in our params, meaning user canceled
    if 'error' in request.GET:
        # redirect to login page with an alert
        request.session.flash(
            u"You must select authorize to continue", 'error')
        return HTTPFound(request.route_url('oauth', action='sign-in'))

    # TODO: validate the `oauth_state` session
    base_url = request.registry.settings['oauth_base_url']
    state = request.GET.get('state')
    client_id = request.registry.settings['oauth_client_id']
    client_secret = request.registry.settings['oauth_secret']
    token_url = "{base_url}{path}".format(
        base_url=base_url,
        path=request.registry.settings['oauth_token_path'])
    redirect_uri = request.route_url('oauth', action='callback')

    session = OAuth2Session(
        client_id,
        state=state,
        redirect_uri=redirect_uri)
    code = request.GET.get('code')
    token = session.fetch_token(
        token_url,
        client_secret=client_secret,
        code=code)

    # retrieve username and store in db if it doesnt exist yet
    user_api_url = "{base_url}{path}".format(
        base_url=base_url,
        path=request.registry.settings['oauth_user_api_path'])
    response = session.request('GET', user_api_url)
    try:
        user_data = json.loads(response.text)
    except ValueError:
        # couldn't decode json
        pass
    else:
        refresh_token = token['refresh_token']
        try:
            user = User.get_or_create_from_api(user_data)
        except ValueError:
            pass
        else:
            request.session['oauth_token'] = json.dumps(token)

            # login user
            headers = remember(request, user.id)

            request.session.flash("Your account has been created, please"
                                  " contact your administrator to activate"
                                  " it", 'error')

            # TODO: redirect to `came_from` url
            return HTTPFound(
                request.route_url(
                    'municipalities', traverse=(), headers=headers))

    request.session.flash(
        u"Failed to login, please try again", 'error')
    return HTTPFound(
        request.route_url('oauth', action='login'))
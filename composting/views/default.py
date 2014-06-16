from pyramid.view import (
    view_config,
)
from pyramid.httpexceptions import HTTPFound


@view_config(route_name='default', renderer='default.jinja2')
def default(request):
    return HTTPFound(request.route_url('municipalities', traverse=()))
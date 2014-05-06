from pyramid.view import (
    view_config,
)


@view_config(route_name='default', renderer='default.jinja2')
def default(request):
    return {}
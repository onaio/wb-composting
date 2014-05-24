from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


def selections_from_request(request, selection_list, comparator, defaults):
    """
    Returns a list of items within selection list that exist within the
    request
    """
    d = dict([(s, comparator(request.GET.get(s))) for s in selection_list])
    status_selection = [k for k, v in d.items() if v is True]
    if len(status_selection) == 0:
        status_selection = defaults
    return status_selection


@view_config(name='update_status_wrapper', request_method='POST')
def update_status(context, request):
    """
    Update the context.submission.status property with the value in
    request.new_status
    """
    # the action we want to target on the municipalities route

    # todo: check that context is a Submission subclass
    if not hasattr(request, 'new_status'):
        raise ValueError(
            "You must set request.new_status to the desired value")

    if not hasattr(context.__class__, 'LIST_URL_SUFFIX'):
        raise ValueError(
            "You must set 'LIST_URL_SUFFIX' on '{}'".format(context.__class__))
    action = context.__class__.LIST_URL_SUFFIX

    municipality_id = context.municipality_submission.municipality_id
    context.status = request.new_status
    context.save()

    return HTTPFound(
        request.route_url(
            'municipalities', traverse=(municipality_id, action)))
def selections_from_request(request, selection_list, comparator, default):
    """
    Returns a list of items within selection list that exist within the
    request
    """
    d = dict([(s, comparator(request.GET.get(s))) for s in selection_list])
    status_selection = [k for k, v in d.items() if v is True]
    if len(status_selection) == 0:
        status_selection = [default]
    return status_selection
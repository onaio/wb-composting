import datetime
import calendar
from collections import defaultdict, OrderedDict
from pyramid.security import authenticated_userid
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound
from pyramid.events import subscriber, NewRequest

from composting.models.user import User
from composting.models.site_report import SiteReport, RATIO


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
    # if the wrapped response is not a 200, return that instead
    if request.wrapped_response.status_code != 200:
        return request.wrapped_response

    # todo: check that context is a Submission subclass
    if not hasattr(request, 'new_status'):
        raise ValueError(
            "You must set request.new_status to the desired value")

    if not hasattr(context.__class__, 'LIST_ACTION_NAME'):
        raise ValueError(
            "You must set 'LIST_ACTION_NAME' on '{}'".format(
                context.__class__))
    action = context.__class__.LIST_ACTION_NAME

    municipality_id = context.municipality_submission.municipality_id
    context.status = request.new_status
    context.save()

    return HTTPFound(
        request.route_url(
            'municipalities', traverse=(municipality_id, action)))


def is_current_path(request, path):
    """
    Return true if path is the current path. Used to set the active css class
    on URLs
    """
    return request.environ['PATH_INFO'] == path


# @todo: move to dashboard
def get_request_user(request):
    user_id = authenticated_userid(request)
    try:
        return User.get(User.id == user_id)
    except NoResultFound:
        return None


@subscriber(NewRequest)
def requested_xlsx_format(event):
    request = event.request
    if request.GET.get('format') == 'xlsx':
        request.override_renderer = 'xlsx'
        return True


def date_from_string_or_default(data, key, default, date_format='%Y-%m-%d'):
    try:
        date_string = data[key]
    except KeyError:
        return default
    return datetime.datetime.strptime(date_string, date_format).date()


def get_start_end_date(data, default_start, default_end, today):
    try:
        start = date_from_string_or_default(
            data, 'start', default_start)
    except ValueError:
        raise HTTPBadRequest("Couldn't parse start date")

    try:
        end = date_from_string_or_default(
            data, 'end', default_end)
    except ValueError:
        raise HTTPBadRequest("Couldn't parse end date")

    # lets not go beyond the current date
    end = min(today, end)

    # start must be less than or equal to end
    if start > end:
        start = end

    return start, end


def get_trend_data(site_reports):
    # generate data format expected by map

    trend_data_list = defaultdict(list)
    trend_data_map = OrderedDict()

    for report in site_reports:
        utc_stamp = calendar.timegm(report.report_date.timetuple()) * 1000
        for key, value in report.report_json.iteritems():
            # adjust ratio values
            if SiteReport.REPORT_VALUE_UNITS[key] == RATIO:
                value = value * 100

            trend_data_list[key].append([utc_stamp, value]
                                        if value
                                        else [utc_stamp, 0])

    for key, value in sorted(trend_data_list.iteritems()):
        label = key.title().replace('Msw', 'MSW').replace('_', ' ')
        label = "{} ({})".format(label, SiteReport.REPORT_VALUE_UNITS[key])
        trend_data_map[key] = {
            'label': label,
            'data': value
        }

    return trend_data_map or None

import datetime
import json

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPForbidden
from pyramid.view import view_defaults, view_config
from deform import Form, ValidationFailure, Button
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound
from dashboard.views.base import BaseView
from dashboard.views.helpers import check_post_csrf

from composting.libs.utils import get_month_start_end
from composting.views.helpers import (
    selections_from_request,
    get_start_end_date,
    get_trend_data)
from composting.models import Municipality, DailyWaste, Submission, Skip
from composting.models.municipality import MunicipalityFactory
from composting.models.monthly_density import MonthlyDensity
from composting.models.monthly_waste_composition import MonthlyWasteComposition
from composting.models.municipality_submission import MunicipalitySubmission
from composting.models.site_report import SiteReport
from composting.forms import SkipForm, SiteProfileForm


@view_defaults(route_name='municipalities', context=Municipality)
class Municipalities(BaseView):

    @view_config(context=MunicipalityFactory,
                 renderer='admin_municipalities_list.jinja2')
    def list(self):
        # if doest have list permissions, determine the user's municipality and
        # redirect, if we cant determine, their municipality, throw a 403
        if not self.request.has_permission('manage', self.request.context):
            municipality = self.request.user.municipality
            if municipality:
                return HTTPFound(
                    self.request.route_url(
                        'municipalities', traverse=(municipality.id,)))
            else:
                return HTTPForbidden(
                    "You don't have permissions to access this page and you do"
                    " not belong to any Municipality")
        municipalities = Municipality.all()
        return {
            'municipalities': municipalities
        }

    @view_config(name='', renderer='municipality_overview.jinja2',
                 permission='show')
    def show(self):
        municipality = self.request.context
        # generate a trend view of saved municipality reports
        # get all site reports belonging to the municipality

        site_reports = SiteReport.all(SiteReport.municipality == municipality)
        trend_data = json.dumps(get_trend_data(site_reports))
        return {
            'municipality': municipality,
            'trend_data': trend_data
        }

    #@view_config(name='daily-waste', renderer='daily_waste_list.jinja2')
    def daily_waste_list(self):
        municipality = self.request.context
        statuses = [Submission.PENDING, Submission.APPROVED,
                    Submission.REJECTED]
        status_selections = selections_from_request(
            self.request,
            statuses,
            lambda status: status == '1',
            [Submission.PENDING, Submission.REJECTED])

        criterion = Submission.status.in_(status_selections)
        daily_wastes = municipality.get_register_records(DailyWaste, criterion)

        status = dict([(s, s in statuses) for s in status_selections])
        return {
            'municipality': municipality,
            'daily_wastes': daily_wastes,
            'status': status
        }

    @view_config(
        name='monthly-waste-density',
        renderer='monthly_waste_density_list.jinja2',
        permission='show')
    def monthly_density_list(self):
        municipality = self.request.context

        # parse date from request if any
        date_string = self.request.GET.get('period')
        if date_string:
            try:
                date = datetime.datetime.strptime(date_string, '%Y-%m')
            except ValueError:
                return HTTPBadRequest("Couldn't understand the date format")
        else:
            date = datetime.datetime.now()

        # determine the date ranges
        start, end = get_month_start_end(date)
        criterion = and_(
            MonthlyDensity.date >= start,
            MonthlyDensity.date <= end)
        municipality_submissions = MunicipalitySubmission.get_items(
            municipality, MonthlyDensity, criterion)
        monthly_densities = [s for ms, s in municipality_submissions]
        average_density = MonthlyDensity.get_average_density(date)

        return {
            'municipality': municipality,
            'items': monthly_densities,
            'average_density': average_density,
            'date': date
        }

    @view_config(
        name='monthly-solid-waste-composition',
        renderer='monthly_waste_composition_list.jinja2',
        permission='show')
    def monthly_waste_composition_list(self):
        municipality = self.request.context

        # parse date from request if any
        date_string = self.request.GET.get('period')
        if date_string:
            try:
                date = datetime.datetime.strptime(date_string, '%Y-%m')
            except ValueError:
                return HTTPBadRequest("Couldn't understand the date format")
        else:
            date = datetime.datetime.now()

        # determine the date ranges
        start, end = get_month_start_end(date)
        criterion = and_(
            MonthlyWasteComposition.date >= start,
            MonthlyWasteComposition.date <= end)
        municipality_submissions = MunicipalitySubmission.get_items(
            municipality, MonthlyWasteComposition, criterion)
        monthly_waste_compositions = [s for ms, s in municipality_submissions]

        # calculate means and percentages
        total_waste_mean = MonthlyWasteComposition.get_total_waste_mean(
            monthly_waste_compositions)
        means = MonthlyWasteComposition.get_means(
            monthly_waste_compositions)
        percentages = MonthlyWasteComposition.get_percentages(
            monthly_waste_compositions)

        return {
            'municipality': municipality,
            'items': monthly_waste_compositions,
            'date': date,
            'total_waste_mean': total_waste_mean,
            'means': means,
            'percentages': percentages
        }

    @view_config(name='skips', renderer='skips.jinja2', permission='show')
    def skips(self):
        municipality = self.request.context
        skips = municipality.get_skips()
        return {
            'skips': skips,
            'municipality': municipality,
        }

    @view_config(name='create-skip', renderer='create_skip.jinja2',
                 permission='edit', decorator=check_post_csrf)
    def create_skip(self):
        municipality = self.request.context
        form = Form(
            SkipForm().bind(
                request=self.request,
                municipality_id=municipality.id),
            buttons=('Save', Button(name='cancel', type='button')))
        if self.request.method == "POST":
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                self.request.session.flash(
                    u"Please fix the errors indicated below.", "error")
            else:
                skip = Skip(municipality=municipality, **values)
                skip.save()
                self.request.session.flash(
                    u"Your changes have been saved.", "success")
                return HTTPFound(
                    self.request.route_url(
                        'skips', traverse=(skip.id, 'edit')))
        return {
            'municipality': municipality,
            'form': form
        }

    @view_config(name='profile', renderer='edit_profile.jinja2',
                 permission='edit', decorator=check_post_csrf)
    def edit_profile(self):
        municipality = self.request.context
        form = Form(
            SiteProfileForm().bind(
                request=self.request),
            buttons=('Save', Button(name='cancel', type='button')),
            appstruct=municipality.appstruct)
        if self.request.method == "POST":
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                self.request.session.flash(
                    u"Please fix the errors indicated below.", "error")
            else:
                municipality.update(**values)
                municipality.save()
                self.request.session.flash(
                    u"Your changes have been saved.", "success")
                return HTTPFound(
                    self.request.route_url(
                        'municipalities',
                        traverse=(municipality.id, 'profile')))
        return {
            'municipality': municipality,
            'form': form
        }

    @view_config(context=MunicipalityFactory, name='create',
                 renderer='add_profile.jinja2', permission='manage',
                 decorator=check_post_csrf)
    def create_profile(self):
        user = self.request.user

        form = Form(
            SiteProfileForm().bind(
                request=self.request),
            buttons=('Save', Button(name='cancel', type='button')))

        if self.request.method == "POST":
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                self.request.session.flash(
                    u"Please fix the errors indicated below.", "error")
            else:
                municipality = Municipality(**values)
                municipality.save()
                user.municipality = municipality
                self.request.session.flash(
                    u"Your changes have been saved.", "success")
                return HTTPFound(
                    self.request.route_url(
                        'municipalities',
                        traverse=(municipality.id, 'profile')))
        return {
            'form': form
        }

    @view_config(name='reports',
                 renderer='site_reports.jinja2',
                 permission='show')
    def site_reports(self):
        municipality = self.request.context
        # default to start and end of current month
        today = datetime.date.today()
        default_start, default_end = get_month_start_end(today)

        start, end = get_start_end_date(
            self.request.GET, default_start, default_end, today)

        # not necessary but pretty format the date range when we can
        if start == default_start and end == default_end:
            label = "This Month"
        elif (today - start).days == 1:
            label = "Yesterday"
        elif end == today:
            time_labels = [
                # if start and end are the same, the label is today
                (lambda dt: dt.days == 0, "Today"),
                # if timedelta between start and end is less than 31 days,
                # last # days
                (lambda dt: 1 < dt.days < 30, "Last {} days")
            ]
            time_delta = today - start
            labels = [l for f, l in time_labels if f(time_delta)]
            label = labels[0].format(time_delta.days + 1)\
                if len(labels) == 1 else None
        else:
            label = None

        # confirm if site report for selected month period is available
        show_save_report = False
        update_report = False

        if (end - start).days <= 31:
            # show save button if the time period selected is a month
            show_save_report = True
            try:
                # try to retrieve month report
                SiteReport.get_report_by_month(end.month, municipality)
                update_report = True
            except NoResultFound:
                pass

        return {
            'municipality': municipality,
            'start': start,
            'end': end,
            'label': label,
            'show_save_report': show_save_report,
            'update_report': update_report
        }

    @view_config(name='save-report',
                 request_method='POST',
                 permission='show')
    def save_site_report(self):
        # get the selected month to create a report for
        # if another report already exists, update it with the report_data
        # contained in the municipality
        today = datetime.date.today()
        default_start, default_end = get_month_start_end(today)
        start, end = get_start_end_date(
            self.request.POST, default_start, default_end, today)

        municipality = self.request.context

        # Populate report_data json
        report_json = municipality.get_data_map(start, end)

        # Get start and end date for the month being reported on
        month_start, month_end = get_month_start_end(start)
        try:
            site_report = SiteReport.get_report_by_month(month_end.month,
                                                         municipality)
            site_report.report_json = report_json
            self.request.session.flash(
                u"The site report has been updated.", "success")
        except NoResultFound:
            site_report = SiteReport(date_created=month_end,
                                     municipality=municipality,
                                     report_json=report_json)
            self.request.session.flash(
                u"The site report has been saved.", "success")

        site_report.save()

        return HTTPFound(self.request.route_url(
            'municipalities',
            traverse=(municipality.id, 'reports'),
            _query={'start': start, 'end': end}))

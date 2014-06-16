import datetime

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.view import view_defaults, view_config
from deform import Form, ValidationFailure, Button
from sqlalchemy import and_

from dashboard.views.base import BaseView

from composting.libs.utils import get_month_start_end
from composting.views.helpers import selections_from_request
from composting.models import Municipality, DailyWaste, Submission, Skip
from composting.models.municipality import MunicipalityFactory
from composting.models.monthly_density import MonthlyDensity
from composting.models.monthly_waste_composition import MonthlyWasteComposition
from composting.models.municipality_submission import MunicipalitySubmission
from composting.forms import SkipForm, SiteProfileForm


@view_defaults(route_name='municipalities', context=Municipality)
class Municipalities(BaseView):
    @view_config(context=MunicipalityFactory,
                 renderer='municipalities_list.jinja2')
    def list(self):
        municipalities = Municipality.all()
        return {
            'municipalities': municipalities
        }

    @view_config(name='', renderer='overview.jinja2')
    def show(self):
        municipality = self.request.context
        return {
            'municipality': municipality
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
        renderer='monthly_waste_density_list.jinja2')
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
        renderer='monthly_waste_composition_list.jinja2')
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


    @view_config(name='skips', renderer='skips.jinja2')
    def skips(self):
        municipality = self.request.context
        skips = municipality.get_skips()
        return {
            'skips': skips,
            'municipality': municipality,
        }

    @view_config(name='create-skip', renderer='create_skip.jinja2')
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

    @view_config(name='profile', renderer='edit_profile.jinja2')
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

    @view_config(name='reports', renderer='site_reports.jinja2')
    def site_reports(self):
        def date_from_string_or_default(
                data, key, default, date_format='%Y-%m-%d'):
            try:
                date_string = data[key]
            except KeyError:
                return default
            return datetime.datetime.strptime(date_string, date_format).date()

        municipality = self.request.context

        # default to start and end of current month
        today = datetime.date.today()
        default_start, default_end = get_month_start_end(today)

        try:
            start = date_from_string_or_default(
                self.request.GET, 'start', default_start)
        except ValueError:
            raise HTTPBadRequest("Couldn't parse start date")

        try:
            end = date_from_string_or_default(
                self.request.GET, 'end', default_end)
        except ValueError:
            raise HTTPBadRequest("Couldn't parse end date")

        # lets not go beyond the current date
        end = min(today, end)

        # start must be less than or equal to end
        if start > end:
            start = end

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
                (lambda dt:  1 < dt.days < 30, "Last {} days")
            ]
            time_delta = today - start
            labels = [l for f, l in time_labels if f(time_delta)]
            label = labels[0].format(time_delta.days + 1)\
                if len(labels) == 1 else None
        else:
            label = None

        return {
            'municipality': municipality,
            'start': start,
            'end': end,
            'label': label
        }
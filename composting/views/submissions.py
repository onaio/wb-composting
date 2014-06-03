import urlparse

from pyramid.view import view_defaults, view_config
from pyramid.response import Response

from dashboard.views.base import BaseView
from dashboard.constants import XFORM_ID_STRING
from composting.models.submission import Submission, ISubmission
from composting.models.municipality_submission import MunicipalitySubmission
from composting.views.helpers import selections_from_request

from pyramid.events import ContextFound
from pyramid.events import subscriber


#@subscriber(ContextFound)
def override_submission_renderer(event):
    """
    Based on the request context, determine the submission renderer to use
    """
    # check if the context provides the ISubmission interface
    if ISubmission.providedBy(event.request.context):
        #event.request.override_renderer = 'json'
        pass

@view_defaults(route_name='submissions', context=ISubmission)
class Submissions(BaseView):
    @view_config(
        route_name='municipalities', name='', renderer='string')
    def list(self):
        model = self.request.context
        municipality = model.__parent__
        self.request.override_renderer = model.renderer()

        # statuses
        all_statuses = [Submission.PENDING, Submission.APPROVED,
                    Submission.REJECTED]
        status_selections = selections_from_request(
            self.request,
            all_statuses,
            lambda status: status == '1',
            [Submission.PENDING, Submission.REJECTED])

        criterion = Submission.status.in_(status_selections)
        municipality_submissions = MunicipalitySubmission.get_items(
            municipality, model.__class__, criterion)
        items = [s for ms, s in municipality_submissions]

        statuses = dict([(s, s in all_statuses) for s in status_selections])
        return {
            'municipality': municipality,
            'items': items,
            'statuses': statuses
        }

    @view_config(name='', renderer='submission_show.jinja2')
    def show(self):
        submission = self.request.context
        self.request.override_renderer = submission.renderer('show')
        image_url_base = urlparse.urljoin(
            'https://ona.io',
            "attachment/small?media_file={}/attachments/".format("wb_composting"))

        data = {}
        return {
            'submission': submission,
            'data': data,
            'image_url_base': image_url_base
        }

    @view_config(name='approve', request_method='POST',
                 wrapper='update_status_wrapper')
    def approve(self):
        self.request.new_status = Submission.APPROVED
        return Response(None)

    @view_config(name='reject', request_method='POST',
                 wrapper='update_status_wrapper')
    def reject(self):
        self.request.new_status = Submission.REJECTED
        return Response(None)

    @view_config(name='unapprove', request_method='POST',
                 wrapper='update_status_wrapper')
    def unapprove(self):
        self.request.new_status = Submission.PENDING
        return Response(None)
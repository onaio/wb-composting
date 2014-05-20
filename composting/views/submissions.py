from pyramid.view import view_defaults, view_config

from dashboard.views.base import BaseView
from composting.models import Municipality
from composting.models.submission import Submission, ISubmission
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

@view_defaults(route_name='municipalities', context=Municipality)
class Submissions(BaseView):
    @view_config(name='', context=ISubmission, renderer='string')
    def list(self):
        model = self.request.context
        municipality = model.__parent__
        self.request.override_renderer = model.renderer

        # statuses
        statuses = [Submission.PENDING, Submission.APPROVED,
                    Submission.REJECTED]
        status_selections = selections_from_request(
            self.request,
            statuses,
            lambda status: status == '1',
            [Submission.PENDING, Submission.REJECTED])

        criterion = Submission.status.in_(status_selections)
        items = model.__class__.get_items()

        status = dict([(s, s in statuses) for s in status_selections])
        return {
            'municipality': municipality,
            'items': items,
            'status': status
        }
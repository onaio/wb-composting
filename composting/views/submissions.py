import logging
import urlparse
import requests

from pyramid.view import view_defaults, view_config
from pyramid.response import Response

from dashboard.views.base import BaseView
from dashboard.views.helpers import check_post_csrf
from composting import constants
from composting.models.submission import Submission, ISubmission
from composting.models.municipality_submission import MunicipalitySubmission
from composting.views.helpers import selections_from_request

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound


#@subscriber(ContextFound)
def override_submission_renderer(event):
    """
    Based on the request context, determine the submission renderer to use
    """
    # check if the context provides the ISubmission interface
    if ISubmission.providedBy(event.request.context):
        # event.request.override_renderer = 'json'
        pass


@view_defaults(route_name='submissions', context=ISubmission)
class Submissions(BaseView):

    @view_config(
        route_name='municipalities',
        name='',
        renderer='string',
        permission='show')
    def list(self):
        model = self.request.context
        municipality = model.__parent__

        # get the renderer from the model
        self.request.override_renderer = model.renderer()

        # statuses
        all_statuses = [Submission.PENDING,
                        Submission.APPROVED,
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
            "attachment/small?media_file={}/attachments/".format(
                "wb_composting"))

        data = {}
        return {
            'submission': submission,
            'data': data,
            'image_url_base': image_url_base
        }

    @view_config(name='approve', request_method='POST',
                 wrapper='update_status_wrapper', decorator=check_post_csrf)
    def approve(self):
        self.request.new_status = Submission.APPROVED
        return Response(None)

    @view_config(name='reject', request_method='POST',
                 wrapper='update_status_wrapper', decorator=check_post_csrf)
    def reject(self):
        self.request.new_status = Submission.REJECTED
        return Response(None)

    @view_config(name='unapprove', request_method='POST',
                 wrapper='update_status_wrapper', decorator=check_post_csrf)
    def unapprove(self):
        self.request.new_status = Submission.PENDING
        return Response(None)

    @view_config(name='edit',
                 request_method='GET')
    def edit(self):
        # redirects to the survey form for specified survey
        submission = self.request.context
        sub_id = submission.json_data[constants.ONA_SUBMISSION_ID]
        form_id = submission.FORM_ID
        return_url = self.request.route_url(
            'submissions', traverse=())
        token = self.request.registry.settings['ona_auth_token']
        url = urlparse.urljoin(
            self.request.registry.settings['ona_data_api'],
            "{}/{}/enketo?return_url={}".format(form_id, sub_id, return_url))

        response = requests.get(
            url,
            headers={"Authorization": "Token {}".format(token)})

        try:
            edit_url = response.json()['url']
        except KeyError:
            logging.getLogger(__name__).error(url)
            logging.getLogger(__name__).error(str(response.json()))
            raise HTTPBadRequest(response.json()['detail'])
        else:
            return HTTPFound(location=edit_url)

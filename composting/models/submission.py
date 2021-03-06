from zope.interface import Interface
from pyramid.security import has_permission, Allow
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    Date,
)
from sqlalchemy import event
from dashboard.libs.utils import date_string_to_datetime, default_date_format

from composting import security
from composting.models.base import Base, DBSession, ModelFactory
from composting.models.report import Report
from composting.constants import SUBMISSION_TIME
from composting.libs.utils import get_locale_time_from_utc_time


class ISubmission(Interface):
    pass


class Submission(Base):
    __tablename__ = 'submissions'

    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    id = Column(Integer, primary_key=True)
    xform_id = Column(String(100), index=True, nullable=False)
    json_data = Column(JSON, nullable=False)
    status = Column(
        Enum(PENDING, APPROVED, REJECTED, name='SUBMISSION_STATUS'),
        nullable=False, index=True, default=PENDING)
    date = Column(Date, nullable=False, server_default='1970-01-01')

    StatusLabels = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    )

    __mapper_args__ = {
        'polymorphic_identity': 'submission',
        'polymorphic_on': xform_id
    }

    DATE_FIELD = 'datetime'
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
    END_FIELD = 'end'

    def __init__(self, request=None, **kwargs):
        if request is not None:
            self.request = request
        super(Submission, self).__init__(**kwargs)

    def __acl__(self):
        # users who have the p:submission-reject permission and the
        # p:submission-reject:<id>
        # in their effective principal's def can reject
        return [
            (Allow, security.SUBMISSION_REJECT_ANY.key, 'reject'),
        ]

    def can_approve(self, request):
        """
        Anyone with permissions can approve if pending AND has valid density
        and tonnage values
        """
        return self.status == Submission.PENDING

    def can_reject(self, request):
        """
        Only NEMA and WB can reject and only after it been approved
        """
        return (self.status == Submission.APPROVED
                and has_permission('reject', self, request))

    def can_unapprove(self, request):
        """
        Only the site manager can un-approve
        """
        return self.status == Submission.APPROVED

    def can_reapprove(self, request):
        """
        Re-approve a previously rejected submission
        """
        return self.status == Submission.REJECTED

    @classmethod
    def get_items_query(cls, *criterion):
        return DBSession.query(cls)\
            .filter(*criterion)

    def renderer(self, type='list'):
        return "{}_{}.jinja2".format(
            self.__mapper_args__['polymorphic_identity'], type)

    @classmethod
    def datetime_from_json(cls, json_data, date_key,
                           date_format=default_date_format):
        """
        Return a datetime object parsed from the specific submission class's
        DATE_FIELD and DATE_FORMAT
        """
        return date_string_to_datetime(json_data[date_key], date_format)

    def time_data(self, key):
        """
        get the datetime object representation of the data within json_data
        with the specified key
        """
        return Submission.datetime_from_json(self.json_data, key)

    @property
    def end_time(self):
        return Submission.datetime_from_json(self.json_data, self.END_FIELD)

    def locale_submission_time(self):
        """
        Convert the submission time, which is in UTC to the specified locale
        """
        submission_time = self.datetime_from_json(
            self.json_data, SUBMISSION_TIME, '%Y-%m-%dT%H:%M:%S')
        return get_locale_time_from_utc_time(submission_time)

    def get_or_create_report(self):
        try:
            report = Report.get(Report.submission == self)
        except NoResultFound:
            return Report(submission=self)
        else:
            return report

    def create_or_update_report(self):
        """
        Will be called whenever the Submission is APPROVED, implement report
        creation logic in subclasses as required
        :return: None
        """
        pass

    def delete_report(self):
        return Report.delete(Report.submission_id == self.id)


def submission_status_set_listener(submission, new_status, old_status, evt):
    if new_status != old_status and old_status in [Submission.PENDING,
                                                   Submission.APPROVED,
                                                   Submission.REJECTED]:
        if new_status == Submission.APPROVED:
            submission.create_or_update_report()
        elif (new_status == Submission.REJECTED
              or new_status == Submission.PENDING):
            submission.delete_report()


event.listen(Submission.status, 'set', submission_status_set_listener,
             propagate=True)


class SubmissionFactory(ModelFactory):
    def __getitem__(self, item):
        from composting.models.municipality_submission import (
            MunicipalitySubmission)
        try:
            submission = DBSession.query(Submission)\
                .join(MunicipalitySubmission)\
                .filter(Submission.id == item)\
                .one()
        except NoResultFound:
            raise KeyError
        else:
            submission.__parent__ = self
            submission.name = item
            return submission

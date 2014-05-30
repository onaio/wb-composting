import pytz
from zope.interface import Interface

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    Date,
)

from composting.constants import SUBMISSION_TIME
from dashboard.libs.utils import date_string_to_datetime, default_date_format

from composting.models.base import Base, DBSession, ModelFactory


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

    def can_approve(self, request):
        """
        Anyone with permissions can approve if pending
        """
        return self.status == Submission.PENDING

    def can_reject(self, request):
        """
        Only NEMA and WB can reject and only after it been approved
        """
        return (self.status == Submission.APPROVED
                and request.GET.get('role') == 'nema')

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
        return self.time_data(Submission.END_FIELD)

    def locale_submission_time(self, tzname="Africa/Kampala"):
        """
        Convert the submission time, which is in UTC to the specified locale
        """
        timezone = pytz.timezone(tzname)
        submission_time = self.datetime_from_json(
            self.json_data, SUBMISSION_TIME, '%Y-%m-%dT%H:%M:%S')
        submission_time = pytz.utc.localize(submission_time)
        return submission_time.astimezone(timezone)


class SubmissionFactory(ModelFactory):
    def __getitem__(self, item):
        try:
            submission = Submission.get(Submission.id == item)
        except NoResultFound:
            raise KeyError
        else:
            submission.__parent__ = self
            submission.name = item
            return submission
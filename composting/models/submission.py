from zope.interface import Interface

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    Date,
)
from dashboard.libs.utils import date_string_to_date

from composting.models.base import Base, DBSession


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

    @property
    def renderer(self):
        return "{}_list.jinja2".format(
            self.__mapper_args__['polymorphic_identity'])

    @classmethod
    def date_from_json(cls, json_data):
        """
        Return a date object parsed from the specific submission class's
        DATE_FIELD and DATE_FORMAT
        """
        return date_string_to_date(
            json_data[cls.DATE_FIELD], cls.DATE_FORMAT)
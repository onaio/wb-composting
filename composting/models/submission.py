from zope.interface import Interface

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

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

    StatusLabels = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    )
    submission_type = Column(
        String(50), nullable=False, server_default='submission', index=True)
    __mapper_args__ = {
        'polymorphic_identity': 'submission',
        'polymorphic_on': submission_type
    }

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

    @classmethod
    def get_items(cls, *criterion):
        return cls.get_items_query(*criterion).all()

    @property
    def renderer(self):
        return "{}_list.jinja2".format(
            self.__mapper_args__['polymorphic_identity'])
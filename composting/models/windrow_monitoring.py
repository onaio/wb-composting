from zope.interface import implementer
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from composting.models.base import RootFactory
from composting.models.submission import Submission, ISubmission


@implementer(ISubmission)
class WindrowMonitoring(Submission):
    __tablename__ = 'windrow_monitorings'

    id = Column(
        Integer, ForeignKey('submissions.id'), primary_key=True)
    windrow_no = Column(String(100), nullable=False, index=True)
    week_no = Column(Integer, nullable=False, index=True)

    XFORM_ID = 'windrow_monitoring_form'
    __mapper_args__ = {
        'polymorphic_identity': XFORM_ID,
    }

    DATE_FIELD = 'date'
    DATE_FORMAT = '%Y-%m-%d'

    WINDROW_NO_FIELD = 'windrow_number'
    WEEK_NO_FIELD = 'week_no'

    LIST_ACTION_NAME = 'windrow-monitoring'
    NO_OF_SAMPLE = 5


class WindrowMonitoringFactory(RootFactory):

    def __getitem__(self, item):
        raise KeyError

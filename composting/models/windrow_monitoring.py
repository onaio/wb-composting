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

    OXYGEN_READING_1 = 'monitoring_group/o1'
    OXYGEN_READING_2 = 'monitoring_group/o2'
    OXYGEN_READING_3 = 'monitoring_group/o3'
    OXYGEN_READING_4 = 'monitoring_group/o4'
    OXYGEN_READING_5 = 'monitoring_group/o5'

    def count_of_low_samples(self):
        # Count all samples within this submission that are below 10%
        oxygen_readings = [self.json_data[self.OXYGEN_READING_1],
                           self.json_data[self.OXYGEN_READING_2],
                           self.json_data[self.OXYGEN_READING_3],
                           self.json_data[self.OXYGEN_READING_4],
                           self.json_data[self.OXYGEN_READING_5]]
        oxygen_readings = map(float, oxygen_readings)
        filtered_o2_readings = [r for r in oxygen_readings if r < 10.0]
        return len(filtered_o2_readings)

    def create_or_update_report(self):
        report = self.get_or_create_report()
        report.report_json = {
            'low_sample_count': self.count_of_low_samples()
        }
        report.submission = self
        report.save()


class WindrowMonitoringFactory(RootFactory):

    def __getitem__(self, item):
        raise KeyError

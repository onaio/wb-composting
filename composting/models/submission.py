from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from composting.models.base import Base


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
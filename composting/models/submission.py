from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    )

from composting.models.base import Base


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    xform_id = Column(String(100), index=True, nullable=False)
    json_data = Column(JSON, nullable=False)
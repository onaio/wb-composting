from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import contains_eager

from composting.models.base import DBSession, Base, ModelFactory
#from composting.models import Submission, DailyWaste


class Municipality(Base):
    __tablename__ = 'municipalities'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    #def __getitem__(self, item):
    #    try:
    #        submission = Submission.get(Submission.id == item)
    #    except NoResultFound:
    #        raise KeyError
    #    else:
    #        submission.__name__ = item
    #        submission.__parent__ = self
    #        return submission

    def get_register_records(self, register_class, *criterion):
        """
        Get records filtered by specified criterion from `register_class`
        eager loading from submissions
        """
        return DBSession.query(register_class)\
            .join(register_class.submission)\
            .filter(*criterion)\
            .options(contains_eager(register_class.submission))\
            .all()


class MunicipalityFactory(ModelFactory):
    def __getitem__(self, item):
        try:
            record = Municipality.get(Municipality.id == item)
        except NoResultFound:
            raise KeyError
        else:
            record.__name__ = item
            record.__parent__ = self
            return record
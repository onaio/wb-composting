from pyramid.security import (
    Allow,
    Authenticated,
    ALL_PERMISSIONS
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from dashboard.models.base import (
    Base, DBSession, BaseRootFactory, BaseModelFactory)


class RootFactory(BaseRootFactory):
    pass


class ModelFactory(BaseModelFactory):
    pass
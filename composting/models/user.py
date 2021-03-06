from pyramid.security import Allow
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey
)
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.orm.exc import NoResultFound

from composting import security
from composting.models.base import Base, ModelFactory
from composting.security import pwd_context


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    pwd = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, server_default='false')
    group = Column(String, nullable=True, server_default=None)
    municipality_id = Column(
        Integer, ForeignKey('municipalities.id'), nullable=True)
    municipality = relationship('Municipality')

    @property
    def password(self):
        return self.pwd

    @password.setter
    def password(self, value):
        from composting.security import pwd_context
        self.pwd = pwd_context.encrypt(value)

    password = synonym('pwd', descriptor=password)

    def check_password(self, password):
        # always return false if password is greater than 255 to avoid
        # spoofing attacks
        if len(password) > 255:
            return False
        return pwd_context.verify(password, self.pwd)

    @property
    def appstruct(self):
        return {
            'group': self.group,
            'municipality_id': self.municipality_id,
            'active': self.active
        }

    def update(self, group, municipality_id, active):
        self.municipality_id = municipality_id
        if group in [security.WB.key, security.NEMA.key]:
            self.municipality_id = None
        self.group = group
        self.active = active
        self.save()

    @classmethod
    def get_or_create_from_api(cls, data):
        username = data['username']
        try:
            user = User.get(User.username == username)
        except NoResultFound:
            user = User(username=username)
            # flash to get the auto-inc id
            user.save()
        return user


class UserFactory(ModelFactory):
    __acl__ = [
        (Allow, security.USER_MANAGE_ALL.key, 'manage')
    ]

    def __getitem__(self, item):
        try:
            record = User.get(User.id == item)
        except NoResultFound:
            raise KeyError
        else:
            record.__name__ = item
            record.__parent__ = self
            record.request = self.request
            return record

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey
)
from sqlalchemy.orm import relationship, synonym

from composting.models.base import DBSession, Base, ModelFactory
from composting.security import pwd_context


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    pwd = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, server_default='false')
    group = Column(String, nullable=False, server_default='sm')
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
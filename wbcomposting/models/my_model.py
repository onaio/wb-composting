from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    )

from wbcomposting.models.base import Base


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

Index('my_index', MyModel.name, unique=True, mysql_length=255)
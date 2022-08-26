from sqlalchemy import Column, Integer, String

from config.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    win = Column(Integer, default=0)
    loss = Column(Integer, default=0)
    draw = Column(Integer, default=0)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.name

    __mapper_args__ = {"eager_defaults": True}

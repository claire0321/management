from sqlalchemy import Column, String

from . import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String(255))
    description = Column(String(255))

from sqlalchemy import Column, String

from app.databases import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255))

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..databases import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255))

    is_active = Column(Boolean, nullable=False, default=True)

    role_id = Column(Integer, ForeignKey("roles.id"), default=3)
    role = relationship("Role", backref="users", uselist=False)

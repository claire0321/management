from sqlalchemy import Column, String

from . import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String(255))
    description = Column(String(255))

    @classmethod
    def get_role_name(cls, role_id: int):
        if role_id == 1:
            return "Admin"
        elif role_id == 2:
            return "Manager"
        elif role_id == 3:
            return "General"
        raise {"message": "Role Not Found"}

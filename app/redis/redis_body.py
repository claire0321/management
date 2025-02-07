from app.databases import user_model, role_model
from app.error.exceptions import RoleException


class UserRedis:
    def __init__(self, user: user_model.User):
        self.user = user

    def serialize(self):
        return {
            "id": self.user.id,
            "username": self.user.username,
            "password": self.user.password,
            "email": self.user.email,
            "created_at": str(self.user.created_at),
            "updated_at": str(self.user.updated_at),
            "is_active": self.user.is_active,
            "role_id": self.user.role_id,
        }

    def get_role_name(self):
        role_id = self.user.role_id
        if role_id == 1:
            return "admin"
        elif role_id == 2:
            return "manager"
        elif role_id == 3:
            return "general"
        raise RoleException(errorCode=f"Role {self.user.role_id} not found")


class RoleRedis:
    def __init__(self, role: role_model.Role):
        self.role = role

    def serialize(self):
        return {
            "id": self.role.id,
            "name": self.role.name,
            "description": self.role.description,
            "created_at": str(self.user.created_at),
            "updated_at": str(self.user.updated_at),
        }

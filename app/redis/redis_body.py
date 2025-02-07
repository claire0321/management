from app.databases import user_model, role_model
from app.error.exceptions import RoleException


class UserRedis:
    def __init__(self, user: user_model.User, role: role_model.Role):
        self.user = user
        self.role = role

    def serialize(self):
        return {
            "id": self.user.id,
            "username": self.user.username,
            "password": self.user.password,
            "email": self.user.email,
            "created_at": self.user.created_at,
            "updated_at": self.user.updated_at,
            "is_active": self.user.is_active,
            "role_id": self.user.role_id,
            "role": RoleRedis(self.role).serialize(),
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
            "created_at": self.role.created_at,
            "updated_at": self.role.updated_at,
            "user": [
                {
                    "id": user.id,
                    "username": user.username,
                    "password": user.password,
                    "email": user.email,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "is_active": user.is_active,
                    "role_id": user.role_id,
                }
                for user in self.role.users
            ],
        }

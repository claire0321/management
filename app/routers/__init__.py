from sqlalchemy.orm import Session

from app.databases import user_model, role_model
from app.error.exceptions import UserException, RoleException


def is_user_exist(username: str, db: Session, active_status: bool = True):
    user = (
        db.query(user_model.User)
        .filter(
            user_model.User.username == username,
            user_model.User.is_active == active_status,
        )
        .first()
    )
    if not user:
        if not active_status:
            raise UserException(errorCode=f"User '{username}' is already in active.")
        raise UserException(errorCode=f"User '{username}' not Found")

    return user


def role_available(role_id: int, db: Session):
    role = db.query(role_model.Role).filter(role_model.Role.id == role_id).first()
    if not role:
        raise RoleException(statusCode=409, errorCode=f"Role {role_id} not found")

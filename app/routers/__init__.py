from sqlalchemy.orm import Session

from app.databases import user_model, role_model
from app.error.exceptions import UserNotFound, UserAlreadyInActive, RoleNotFound


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
            raise UserAlreadyInActive(username)
        raise UserNotFound(username)

    return user


def role_available(role_id: int, db: Session):
    role = db.query(role_model.Role).filter(role_model.Role.id == role_id).first()
    if not role:
        raise RoleNotFound(role_id=role_id)

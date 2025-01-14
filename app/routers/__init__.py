from sqlalchemy.orm import Session

from ..databases import user_model
from app.error.exceptions import UserNotFound


def is_user_exist(username: str, db: Session):
    user = (
        db.query(user_model.User).filter(user_model.User.username == username).first()
    )

    if not user:
        raise UserNotFound(username)
    return user

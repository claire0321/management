import json
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.databases import user_model, role_model
from app.error.exceptions import UserException, RoleException
from app.models import schemas
from app.redis import redis_cache, redis_set


# import json
# from app.redis import redis_cache, redis_body


def prev_is_user_exist(username: str, db: Session, active_status: bool = True):
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


def is_user_exist(username: str, db: Session, active_status: bool = True):
    cache_key = f"Users:{username}"
    cache_user = redis_cache.get(cache_key)
    if cache_user:
        user_data = json.loads(cache_user.decode("utf-8"))
        return datetime_parser(user_data)

    # Search From db
    user = (
        db.query(user_model.User)
        .filter(
            user_model.User.username == username,
            user_model.User.is_active == active_status,
        )
        .first()
    )
    if not user:
        raise UserException(
            errorCode=(
                f"User '{username}' is already in active."
                if not active_status
                else f"User '{username}' not Found"
            )
        )

    # Caching to redis
    user_data = {k: v for k, v in user.__dict__.items() if not k.startswith("_")}
    redis_set("user", username, user_data)
    return user_data


def datetime_parser(data: dict):
    for key, value in data.items():
        if key == "role":
            data["role"] = datetime_parser(value)
        if isinstance(value, str):
            try:
                data[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return data


def role_available(role_id: int, db: Session):
    role = db.query(role_model.Role).filter(role_model.Role.id == role_id).first()
    if not role:
        raise RoleException(statusCode=409, errorCode=f"Role {role_id} not found")


def sorting_user(sort_by: Optional[schemas.SortByQuery], order_by: Optional[schemas.OrderQuery], query):
    if sort_by == "role_id":
        sort_field = user_model.User.role_id
    else:
        sort_field = user_model.User.username

    if order_by == "desc":
        query = query.order_by(desc(sort_field))
    elif order_by == "asc":
        query = query.order_by(asc(sort_field))

    return query.all()

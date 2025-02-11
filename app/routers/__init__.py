import json
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.databases import user_model, role_model
from app.databases.redis_base import redis_cache, redis_set
from app.error.exceptions import VariableException
from app.models import schemas


# TODO: CRUD user 랑 role 둘다 쓸 수 있게 만들어 보기.
async def is_user_exist(username: str, db: Session, active_status: bool = True):
    async def datetime_parser(data: dict):
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    data[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass
        return data

    user = None
    cache_key = f"USER:{username}"
    cache_user = redis_cache.get(cache_key)
    if cache_user:
        user_data = json.loads(cache_user)
        return await datetime_parser(user_data), user

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
        raise VariableException(
            errorCode=(
                f"User '{username}' is already in active."
                if not active_status
                else f"User '{username}' not Found"
            )
        )

    # Caching to redis
    user_data = {k: v for k, v in user.__dict__.items() if not k.startswith("_")}
    redis_set("user", username, user_data)
    return user_data, user


async def role_available(role_id: int, db: Session):
    role = db.query(role_model.Role).filter(role_model.Role.id == role_id).first()
    if not role:
        raise VariableException(statusCode=409, errorCode=f"Role {role_id} not found")


async def sorting_user(
        query, order_by: Optional[schemas.OrderQuery],
        sort_by: Optional[schemas.SortByQuery]
):
    def get_sort_value(user):
        value = getattr(user, sort_by)
        if isinstance(value, str):
            return value.lower()
        return value

    if not sort_by and order_by:  # order_by 만 있는 경우
        sort_by = "username"
    elif not order_by and sort_by:  # sort_by 만 있는 경우ㅉ
        return sorted(query, key=get_sort_value)

    # 둘다 있는 경우
    if order_by == "desc":
        return sorted(query, key=get_sort_value, reverse=True)
    elif order_by == "asc":
        return sorted(query, key=get_sort_value)
    else:  # 아무것도 없는 경우
        return query

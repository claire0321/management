import json

from sqlalchemy.orm import Session

from app.databases import user_model, role_model
from app.error.exceptions import UserException, RoleException
from app.redis import redis_cache, redis_body


def is_user_exist(username: str, db: Session, active_status: bool = True):
    cache_user = redis_cache.get(f"Users:{username}")
    if cache_user:
        return json.loads(cache_user.decode("utf-8"))

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
        if not active_status:
            raise UserException(errorCode=f"User '{username}' is already in active.")
        raise UserException(errorCode=f"User '{username}' not Found")

    # Caching to redis
    user_data = redis_body.UserRedis(user).serialize()
    user_redis = json.dumps(user_data, ensure_ascii=False).encode("utf-8")
    redis_cache.set(name=f"Users:{username}", value=user_redis, ex=180)
    return user_data


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

import json
import os

import redis
from dotenv import load_dotenv

from app.databases import role_model, user_model
from app.databases.database import db_dependency
from app.redis.redis_body import RoleRedis, UserRedis

load_dotenv()


def redis_connect():
    try:
        REDIS_HOST: str = os.getenv("REDIS_HOST")
        REDIS_POST: int = os.getenv("REDIS_PORT")
        REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")
        REDIS_DATABASE: int = os.getenv("REDIS_DATABASE")
        rd = redis.Redis(host=REDIS_HOST, port=REDIS_POST, password=REDIS_PASSWORD, db=REDIS_DATABASE)
        return rd
    except redis.exceptions:
        print("Redis connection failure")


def redis_set(type_: str = "user", id_: str = None, data: dict = None, ex=180):
    try:
        key = f"{type_.upper()}:{id_}"
        value = json.dumps(data, ensure_ascii=False, default=str)
        redis_cache.set(key, value, ex)
    except:
        raise


def redis_refresh(db: db_dependency):
    user_query = db.query(user_model.User.username).filter(user_model.User.is_active == 1)
    usernames = [user.username for user in user_query.all()]
    cached_users = []
    missing_users = []

    role_query = db.query(role_model.Role.name)
    roles = [role.name for role in role_query.all()]
    cached_roles = []
    missing_roles = []

    for username in usernames:
        cache_key = f"USER:{username}"
        cache_data = redis_cache.get(cache_key)
        if cache_data:
            cached_users.append(json.loads(cache_data))
        else:
            missing_users.append(username)

    for role in roles:
        cache_key = f"ROLE:{role}"
        cache_data = redis_cache.get(cache_key)
        if cache_data:
            cached_roles.append(json.loads(cache_data))
        else:
            missing_roles.append(role)

    if not missing_users and not missing_roles:
        print({"message": "Everything is updated"})
        return cached_users, cached_roles

    if missing_users:
        db_users = db.query(user_model.User).filter(user_model.User.username.in_(missing_users)).all()
        for user in db_users:
            user_data = {k: v for k, v in user.__dict__.items() if not k.startswith("_")}
            redis_set(id_=user.username, data=user_data)
            cached_users.append(user_data)
    if missing_roles:
        db_roles = db.query(role_model.Role).filter(role_model.Role.name.in_(missing_roles)).all()
        for role in db_roles:
            role_data = {k: v for k, v in role.__dict__.items() if not k.startswith("_")}
            redis_set(type_="role", id_=role.name, data=role_data)
            cached_roles.append(role_data)

    return cached_users, cached_roles


redis_cache = redis_connect()

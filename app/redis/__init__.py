import json
import os

import redis
from dotenv import load_dotenv

from app.databases import role_model
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


def redis_init(db: db_dependency):
    roles = db.query(role_model.Role).all()
    roles_data = []
    for role in roles:
        role_data = RoleRedis(role).serialize()


def redis_set(type_: str, id_, data: dict, ex=180):
    key = f"{type_.upper()}:{id_}"
    value = json.dumps(data, ensure_ascii=False, default=str)
    redis_cache.set(key, value, ex)


redis_cache = redis_connect()

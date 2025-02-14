import json
import os

import redis
from dotenv import load_dotenv

from app.error import RedisException

load_dotenv()

global rd


class RedisSetting:
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_POST: int = os.getenv("REDIS_PORT")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")
    REDIS_DATABASE: int = os.getenv("REDIS_DATABASE")


def redis_connect():
    try:
        global rd
        rd = redis.Redis(host=RedisSetting.REDIS_HOST, port=RedisSetting.REDIS_POST,
                         db=RedisSetting.REDIS_DATABASE)
        print("Redis connection success")
        return rd
    except redis.exceptions:
        print("Redis connection failure")


def redis_set(type_: str = "user", id_: str = None, db=None, ex=1800):
    try:
        global rd
        key = f"{type_.upper()}:{id_}"
        data: dict = db.__dict__.copy()
        data.pop("_sa_instance_state")
        value = json.dumps(data, ensure_ascii=False, default=str, indent=2).encode("utf-8")
        rd.set(key, value, ex)
        print(f"Redis set: {key}")
    except:
        print("Redis set failure")
        raise


def redis_get(types: str = "user", name: str = None):
    try:
        global rd
        cache_key = f"{types.upper()}:{name}"
        cache_data = rd.get(cache_key)
        if not cache_data:
            print(f"Redis {cache_key} not found")
            return None
        data = json.loads(cache_data.decode("utf-8"))
        print(f"Redis get: {cache_key}")
        return data
    except:
        print("Redis get failure")
        raise RedisException(errorCode="Enable to get redis")


def redis_disconnect():
    global rd
    rd.connection_pool.disconnect()
    print("Redis disconnected")


def redis_rd():
    global rd
    return rd


def redis_delete(key):
    global rd
    try:
        rd.delete(key)
        print(f"Redis delete: {key}")
    except:
        print(f"Redis delete failure")
        raise RedisException(errorCode=f"Enable to delete '{key}'")

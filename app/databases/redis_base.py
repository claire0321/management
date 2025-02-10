import json
import os

from dotenv import load_dotenv

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


def redis_set(type_: str = "user", id_: str = None, data: dict = None, ex=1800):
    try:
        key = f"{type_.upper()}:{id_}"
        value = json.dumps(data, ensure_ascii=False, default=str)
        redis_cache.set(key, value, ex)
    except:
        raise


redis_cache = redis_connect()

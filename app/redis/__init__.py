import os

import redis
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


redis_cache = redis_connect()

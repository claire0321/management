import os
from pathlib import Path

from dotenv import load_dotenv

dir_path = (Path(__file__) / ".." / "..").resolve()
env_path = os.path.join(dir_path, ".env")
load_dotenv(dotenv_path=env_path)


class DbSetting:
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASSWORD")
    HOST = os.getenv("DB_HOST")
    PORT = os.getenv("DB_PORT")
    DATABASE = os.getenv("DB_NAME")

    SQLALCHAMY_DATABASE_URL = os.getenv("SQLALCHAMY_DATABASE_URL")


class JwtSetting:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


db_settings = DbSetting()
jwt_settings = JwtSetting()

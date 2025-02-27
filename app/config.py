# import os
# from pathlib import Path
#
# from dotenv import load_dotenv
#
# dir_path = (Path(__file__) / ".." / "..").resolve()
# env_path = os.path.join(dir_path, ".env")
# load_dotenv(dotenv_path=env_path)
#
#
# class DbSetting:
#     USER = os.getenv("DB_USER")
#     PASSWORD = os.getenv("DB_PASSWORD")
#     HOST = os.getenv("DB_HOST")
#     PORT = os.getenv("DB_PORT")
#     DATABASE = os.getenv("DB_NAME")
#
#     SQLALCHAMY_DATABASE_URL = os.getenv("SQLALCHAMY_DATABASE_URL")
#
#
# class JwtSetting:
#     SECRET_KEY = os.getenv("SECRET_KEY")
#     ALGORITHM = os.getenv("ALGORITHM")
#     ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
#
#

# db_settings = DbSetting()
# jwt_settings = JwtSetting()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class DatabaseSetting(Settings):
    DB_CONNECTION: str
    DB_HOST: str
    DB_PORT: str
    DB_DATABASE: str
    DB_USERNAME: str
    DB_PASSWORD: str


class JWTSetting(Settings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str


class TestMessageCli:
    @staticmethod
    def start(function: str, n: int):
        print(f"┌--{'-' * (n + 15)}--┐")
        print(f"   <{function} starts...>")
        # print("<---------------------------------->")

    @staticmethod
    def finish(function: str, n: int):
        # print("<---------------------------------->")
        print(f"   <{function} finished...>")
        print(f"└--{'-' * (n + 15)}--┘")

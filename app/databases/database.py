from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import DatabaseSetting


@lru_cache()
def setting():
    return DatabaseSetting()


def database_mysql_url_config():
    return str(
        setting().DB_CONNECTION
        + "://"
        + setting().DB_USERNAME
        + ":"
        + setting().DB_PASSWORD
        + "@"
        + setting().DB_HOST
        + ":"
        + setting().DB_PORT
        + "/"
        + setting().DB_DATABASE
    )


DB_URL = database_mysql_url_config()

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency Injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

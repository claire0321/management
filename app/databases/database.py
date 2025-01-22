from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import db_settings

DB_URL = f"mysql+pymysql://{db_settings.USER}:{db_settings.PASSWORD}@{db_settings.HOST}:{db_settings.PORT}/{db_settings.DATABASE}"
# DB_URL = db_settings.SQLALCHAMY_DATABASE_URL

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

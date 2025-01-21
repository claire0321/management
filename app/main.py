from fastapi import FastAPI

from app.databases import Base
from app.databases.database import engine
from app.error import exception_handler
from app.middleware import init_middleware
from app.routers import authentication, users, roles

app = FastAPI()

Base.metadata.create_all(bind=engine)


def init_router():
    app.include_router(authentication.router)
    app.include_router(users.router)
    app.include_router(roles.router)


def create_app():
    init_router()
    init_middleware(app)
    exception_handler(app)


create_app()

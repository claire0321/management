# https://www.youtube.com/watch?v=ZX4I6xginvc
# https://www.youtube.com/watch?v=-AM5QVkb0OM
from fastapi import FastAPI

from app.databases import Base
from app.databases.database import engine
from app.error.error_handler import (
    not_found_exception_handler,
    auth_error_handler,
    user_already_active_exception_handler,
    empty_field_exception_handler,
    invalid_username_not_alphanum_exception_handler,
    invalid_data_type_exception_handler,
)
from app.error.exceptions import *
from app.middleware import auth_middleware
from app.routers import authentication, users, roles

app = FastAPI()

Base.metadata.create_all(bind=engine)


def init_router():
    app.include_router(authentication.router)
    app.include_router(users.router)
    app.include_router(roles.router)


def init_middleware():
    app.add_middleware(auth_middleware.AuthorizationMiddleware)
    app.add_middleware(auth_middleware.AuthenticationMiddleware, on_error=auth_error_handler)


def exception_handler():
    app.add_exception_handler(UserNotFound, not_found_exception_handler)
    app.add_exception_handler(UserAlreadyInActive, user_already_active_exception_handler)
    app.add_exception_handler(EmptyField, empty_field_exception_handler)
    app.add_exception_handler(InvalidUsername, invalid_username_not_alphanum_exception_handler)
    app.add_exception_handler(InvalidDataType, invalid_data_type_exception_handler)


def create_app():
    init_router()
    init_middleware()
    exception_handler()


create_app()

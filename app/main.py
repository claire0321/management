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
    insufficient_space_exception_handler,
    not_unique_username_exception_handler,
    # invalid_credentials_exception_handler,
    invalid_token_exception_handler,
    role_not_found,
)
from app.error.exceptions import (
    AuthBackendException,
    UserNotFound,
    UserAlreadyExists,
    UserAlreadyInActive,
    EmptyField,
    InvalidUsername,
    InvalidDataType,
    InsufficientSpace,
    # InvalidCredentials,
    InvalidToken,
    RoleNotFound,
)
from app.middleware import auth_middleware
from app.routers import authentication, users, roles

app = FastAPI()

Base.metadata.create_all(bind=engine)


def init_router():
    app.include_router(authentication.router)
    app.include_router(users.router)
    app.include_router(roles.router)


def init_middleware():
    exception_handlers = {
        AuthBackendException: auth_error_handler,
        InvalidToken: invalid_token_exception_handler,
        # InvalidCredentials: invalid_credentials_exception_handler,
        RoleNotFound: role_not_found,
    }

    app.add_middleware(auth_middleware.AuthorizationMiddleware)
    app.add_middleware(auth_middleware.AuthenticationMiddleware, on_error=exception_handlers)


def exception_handler():
    app.add_exception_handler(UserNotFound, not_found_exception_handler)
    app.add_exception_handler(UserAlreadyInActive, user_already_active_exception_handler)
    app.add_exception_handler(EmptyField, empty_field_exception_handler)
    app.add_exception_handler(InvalidUsername, invalid_username_not_alphanum_exception_handler)
    app.add_exception_handler(InvalidDataType, invalid_data_type_exception_handler)
    app.add_exception_handler(InsufficientSpace, insufficient_space_exception_handler)
    app.add_exception_handler(UserAlreadyExists, not_unique_username_exception_handler)


def create_app():
    init_router()
    init_middleware()
    exception_handler()


create_app()

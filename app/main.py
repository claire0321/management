# https://www.youtube.com/watch?v=ZX4I6xginvc
# https://www.youtube.com/watch?v=-AM5QVkb0OM
from fastapi import FastAPI

from app.databases import Base
from app.databases.database import engine
from app.middleware import auth_middleware
from app.routers import authentication, users, roles
from app.error.error_handler import not_found_exception_handler, auth_error_handler
from app.error.exceptions import UserNotFound
from fastapi.exceptions import HTTPException

app = FastAPI()

Base.metadata.create_all(bind=engine)


def init_router():
    app.include_router(authentication.router)
    app.include_router(users.router)
    app.include_router(roles.router)


def init_middleware():
    app.add_middleware(
        auth_middleware.AuthorizationMiddleware,
        on_error=auth_error_handler,
    )
    app.add_middleware(auth_middleware.AuthenticationMiddleware)


def exception_handler():
    app.add_exception_handler(UserNotFound, not_found_exception_handler)
    pass


def create_app():
    init_router()
    init_middleware()
    exception_handler()


create_app()

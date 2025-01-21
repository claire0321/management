from fastapi import FastAPI

from app.error.error_handler import (
    auth_error_handler,
    invalid_token_exception_handler,
    role_not_found_exception_handler,
)
from app.error.exceptions import (
    AuthBackendException,
    InvalidToken,
    RoleNotFound,
)
from app.middleware import auth_middleware


def init_middleware(app: FastAPI):
    exception_handlers = {
        AuthBackendException: auth_error_handler,
        InvalidToken: invalid_token_exception_handler,
        RoleNotFound: role_not_found_exception_handler,
    }

    app.add_middleware(auth_middleware.AuthorizationMiddleware)
    app.add_middleware(auth_middleware.AuthenticationMiddleware, on_error=exception_handlers)

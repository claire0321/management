from fastapi import FastAPI

from app.error.error_handler import (
    auth_error_handler, variable_error_handler
)
from app.error.exceptions import AuthBackendException, VariableException
from app.middleware import auth_middleware


def init_middleware(app: FastAPI):
    exception_handlers = {
        AuthBackendException: auth_error_handler,
        VariableException: variable_error_handler,
    }

    app.add_middleware(auth_middleware.AuthorizationMiddleware)
    app.add_middleware(auth_middleware.AuthenticationMiddleware, on_error=exception_handlers)

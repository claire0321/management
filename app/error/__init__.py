from fastapi import FastAPI

from app.error.error_handler import (
    user_error_handler,
    field_error_handler,
    role_error_handler,
)
from app.error.exceptions import UserException, FieldException, RoleException


def exception_handler(app: FastAPI):
    app.add_exception_handler(UserException, user_error_handler)
    app.add_exception_handler(FieldException, field_error_handler)
    app.add_exception_handler(RoleException, role_error_handler)

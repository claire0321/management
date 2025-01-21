from fastapi import FastAPI

from app.error.error_handler import (
    not_found_exception_handler,
    auth_error_handler,
    user_already_active_exception_handler,
    empty_field_exception_handler,
    invalid_username_not_alphanum_exception_handler,
    invalid_data_type_exception_handler,
    insufficient_space_exception_handler,
    not_unique_username_exception_handler,
    invalid_token_exception_handler,
    role_not_found_exception_handler,
    insufficient_permission_exception_handler,
    role_already_exists_exception_handler,
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
    InsufficientPermission,
    InvalidToken,
    RoleNotFound,
    RoleAlreadyExists,
)


def exception_handler(app: FastAPI):
    app.add_exception_handler(UserNotFound, not_found_exception_handler)
    app.add_exception_handler(UserAlreadyInActive, user_already_active_exception_handler)
    app.add_exception_handler(EmptyField, empty_field_exception_handler)
    app.add_exception_handler(InvalidUsername, invalid_username_not_alphanum_exception_handler)
    app.add_exception_handler(InvalidDataType, invalid_data_type_exception_handler)
    app.add_exception_handler(InsufficientSpace, insufficient_space_exception_handler)
    app.add_exception_handler(UserAlreadyExists, not_unique_username_exception_handler)
    app.add_exception_handler(InsufficientPermission, insufficient_permission_exception_handler)
    app.add_exception_handler(RoleAlreadyExists, role_already_exists_exception_handler)

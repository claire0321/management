from fastapi import Request
from starlette.responses import JSONResponse

from app.error.exceptions import (
    AuthBackendException,
    UserNotFound,
    UserAlreadyExists,
    UserAlreadyInActive,
    EmptyField,
    InvalidUsername,
    InvalidDataType,
    InsufficientSpace,
    InvalidToken,
    RoleNotFound,
    InsufficientPermission,
    RoleAlreadyExists,
    MissingValue,
)


async def auth_error_handler(request: Request, exc: AuthBackendException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode}, headers=exc.headers)


async def not_found_exception_handler(request: Request, exc: UserNotFound):
    return JSONResponse(status_code=409, content={"ERROR": f"User '{exc.username}' not Found"})


async def not_unique_username_exception_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=409,
        content={"ERROR": f"Username '{exc.username}' already exists"},
    )


async def user_already_active_exception_handler(request: Request, exc: UserAlreadyInActive):
    return JSONResponse(status_code=409, content={"ERROR": f"User '{exc.username}' is already in active."})


async def empty_field_exception_handler(request: Request, exc: EmptyField):
    return JSONResponse(
        status_code=422,
        content={"ERROR": f"{exc.field} cannot be empty"},
    )


async def invalid_username_not_alphanum_exception_handler(request, exc: InvalidUsername):
    return JSONResponse(
        status_code=422,
        content={"ERROR": f"Username should be alphanum."},
    )


async def invalid_data_type_exception_handler(request: Request, exc: InvalidDataType):
    return JSONResponse(
        status_code=422,
        content={"ERROR": "Validation Error. Please provide a valid data type."},
    )


async def insufficient_space_exception_handler(request: Request, exc: InsufficientSpace):
    return JSONResponse(
        status_code=422,
        content={"ERROR": f"Validation Error. Please provide value without any space in {exc.field}."},
    )


async def invalid_token_exception_handler(request, exc: InvalidToken):
    return JSONResponse(
        status_code=403,
        content={"ERROR": "Invalid Token"},
    )


async def role_not_found_exception_handler(request: Request, exc: RoleNotFound):
    error_message = "Role Not Found"

    if exc.token_name:
        error_message = f"Role for '{exc.token_name}' not found"
    elif exc.role_id:
        error_message = f"Role {exc.role_id} not found"

    return JSONResponse(status_code=409, content={"ERROR": error_message})


async def insufficient_permission_exception_handler(request: Request, exc: InsufficientPermission):
    error_message = "Invalid values to be updated"
    status_code = 409
    if exc.errorCode:
        error_message = exc.errorCode
    if exc.statusCode:
        status_code = 403
    return JSONResponse(status_code=status_code, content={"ERROR": error_message})


async def role_already_exists_exception_handler(request: Request, exc: RoleAlreadyExists):
    return JSONResponse(status_code=409, content={"ERROR": f"Role '{exc.role_name}' already exists"})


async def missing_value_exception_handler(request: Request, exc: MissingValue):
    return JSONResponse(status_code=422, content={"ERROR": f"Field '{exc.field}' is missing or required."})

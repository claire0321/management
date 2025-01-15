from fastapi import Request
from starlette.responses import JSONResponse

from app.error.exceptions import *


def auth_error_handler(request: Request, exc: AuthBackendException):
    return JSONResponse(
        {"ERROR": "Incorrect username or password"},
        401,
        {"WWW-Authenticate": "Bearer"},
    )


async def not_found_exception_handler(request: Request, exc: UserNotFound):
    return JSONResponse(status_code=409, content={"ERROR": f"User '{exc.username}' not Found"})


async def not_unique_username_exception_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=409,
        content={"ERROR": f"Username '{exc.username}' already exists"},
    )


async def user_already_active_exception_handler(request: Request, exc: UserNotFound):
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


async def invalid_data_type_exception_handler(request: Request, exc: EmptyField):
    return JSONResponse(
        status_code=422,
        content={"ERROR": "Validation Error. Please provide a valid data type."},
    )


async def insufficient_space_exception_handler(request: Request, exc: InsufficientSpace):
    return JSONResponse(
        status_code=422,
        content={"ERROR": f"Validation Error. Please provide value without any space in {exc.field}."},
    )

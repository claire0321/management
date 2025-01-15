from fastapi import Request, status
from pydantic import ValidationError
from starlette.responses import JSONResponse
from app.error.exceptions import *

from app.error import AuthBackendException


def auth_error_handler(request: Request, exc: AuthBackendException):
    return JSONResponse(
        "Incorrect username or password",
        401,
        {"WWW-Authenticate": "Bearer"},
    )


async def not_found_exception_handler(request: Request, exc: UserNotFound):
    return JSONResponse(status_code=409, content=f"User '{exc.username}' not Found")


async def user_already_active_exception_handler(request: Request, exc: UserNotFound):
    return JSONResponse(
        status_code=409, content=f"User '{exc.username}' is already in active."
    )


async def empty_field_exception_handler(request: Request, exc: EmptyField):
    return JSONResponse(
        status_code=422,
        content=f"{exc.field} cannot be empty",
    )


async def invalid_username_not_alphanum_exception_handler(
    request, exc: InvalidUsername
):
    return JSONResponse(
        status_code=422,
        content=f"Username should be alphanum.",
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = [{"field": err["loc"][0], "message": err["msg"]} for err in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"message": "Validation Error", "details": errors},
    )

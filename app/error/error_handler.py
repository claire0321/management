from fastapi import Request
from starlette.responses import JSONResponse

from app.error.exceptions import AuthBackendException, UserException, FieldException, RoleException


async def auth_error_handler(request: Request, exc: AuthBackendException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode}, headers=exc.headers)


async def user_error_handler(request: Request, exc: UserException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode})


async def field_error_handler(request: Request, exc: FieldException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode})


async def role_error_handler(request: Request, exc: RoleException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode})

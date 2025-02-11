from fastapi import Request
from starlette.responses import JSONResponse

from app.error.exceptions import AuthBackendException, FieldException, VariableException


async def auth_error_handler(request: Request, exc: AuthBackendException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode}, headers=exc.headers)


async def variable_error_handler(request: Request, exc: VariableException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode})


async def field_error_handler(request: Request, exc: FieldException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode})

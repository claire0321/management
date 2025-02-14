from fastapi import Request
from starlette.responses import JSONResponse

from app.error.exceptions import AuthBackendException, FieldException, VariableException, RedisException


async def auth_error_handler(request: Request, exc: AuthBackendException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode}, headers=exc.headers)


async def variable_error_handler(request: Request, exc: VariableException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode})


async def field_error_handler(request: Request, exc: FieldException):
    return JSONResponse(status_code=exc.statusCode, content={"ERROR": exc.errorCode})


async def redis_error_handler(request: Request, exe: RedisException):
    return JSONResponse(status_code=exe.statusCode, content={"ERROR": exe.errorCode})

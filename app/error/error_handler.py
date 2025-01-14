from fastapi import Request
from fastapi.exceptions import HTTPException
from starlette.responses import JSONResponse
from app.error.exceptions import UserNotFound


def auth_error_handler():
    pass


async def not_found_exception_handler(request: Request, exc: UserNotFound):
    return JSONResponse(status_code=409, content=f"User '{exc.username}' not Found")

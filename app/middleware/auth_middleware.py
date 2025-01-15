from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.authorization import token
from app.models import schemas
from app.error import AuthBackendException

BASIC_PATH = ["/docs", "/openapi.json", "/favicon.ico"]


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, on_error=None):
        super().__init__(app)
        self.on_error = on_error

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            if "login" in request.url.path:
                author = response.headers.get("Authorization")
                if not author:
                    raise AuthBackendException()
                token_type, access_token = author.split(" ")
                return JSONResponse(
                    content={"token_type": token_type, "access_token": access_token},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return response
        except AuthBackendException as e:
            # Handle specific AuthBackendException
            if self.on_error:
                return self.on_error(request, e)
        except ValidationError as e:
            if self.on_error:
                return self.on_error(request, e)


class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if "login" not in path and path not in BASIC_PATH:
            auth = request.headers.get("authorization")
            if auth:
                token_data = token.verify_token(auth)
                if not isinstance(token_data, schemas.TokenData):
                    return JSONResponse("Token Expired", 403)
                if request.method != "GET" and token_data.role_id == 3:
                    return JSONResponse(
                        "Not Authorization", 403, {"WWW-Authenticate": "Bearer"}
                    )
            else:
                return JSONResponse(
                    "Not Authorized", 403, {"WWW-Authenticate": "Bearer"}
                )
        response = await call_next(request)
        return response

import re

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.authorization import token
from app.error.exceptions import AuthBackendException, InvalidToken, RoleNotFound

BASIC_PATH = ["/docs", "/openapi.json", "/favicon.ico"]


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, on_error=None):
        super().__init__(app)
        self.on_error = on_error or {}

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            if "login" in request.url.path:
                author = response.headers.get("Authorization")
                if not author:
                    raise AuthBackendException
                token_type, access_token = author.split(" ")
                return JSONResponse(
                    content={"token_type": token_type, "access_token": access_token},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return response
        except AuthBackendException as e:
            handler = self.on_error.get(type(e))
            if handler:
                return handler(request, e)
        except (InvalidToken, RoleNotFound) as e:
            handler = self.on_error.get(type(e))
            if handler:
                return await handler(request, e)
            return JSONResponse(status_code=400, content={"detail": f"Error: {str(e)}"})


class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.role_access = {
            "admin": {"users": ["POST", "GET", "PUT", "DELETE"], "role": ["POST", "PUT", "GET"]},
            "manager": {"users": ["POST", "GET", "PUT", "DELETE"]},
            "general": {"users": ["GET"]},
        }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if "login" not in path and path not in BASIC_PATH:
            auth = request.headers.get("authorization")
            if auth:
                token_data = token.verify_token(auth)
                role = token_data.get_role_name(token_data.role_id)
                tags = path_tags(path)
                if (
                    role in self.role_access
                    and tags in self.role_access[role]
                    and request.method in self.role_access[role][tags]
                ):
                    pass
                else:
                    raise AuthBackendException(errorCode="Not Authorized", statusCode=403)
            else:
                raise AuthBackendException(errorCode="Not Authorized", statusCode=403)
        response = await call_next(request)
        return response


def path_tags(path):
    match = re.match(r"^/([^/]+)", path)
    if match:
        return match.group(1)
    return None

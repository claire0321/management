from http.client import responses

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from starlette.responses import JSONResponse

from ..authorization import token
from ..models import schemas

BASIC_PATH = ["/docs", "/openapi.json", "/favicon.ico"]


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if "login" in request.url.path:
            author = response.headers.get("Authorization")
            if not author:
                return JSONResponse(
                    "Incorrect username or password",
                    401,
                    {"WWW-Authenticate": "Bearer"},
                )
            token_type, access_token = author.split(" ")
            return JSONResponse(
                content={"token_type": token_type, "access_token": access_token},
                headers={"WWW-Authenticate": "Bearer"},
            )
        return response


class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, on_error=None):
        super().__init__(app)
        self.on_error = on_error

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
        #
        # if request.method == "GET" and request.url.path in BASIC_PATH:
        #     response = await call_next(request)  # Make sure `call_next` is not None
        #     return response
        #
        # response = await call_next(request)
        # auth = request.headers.get("authorization")
        #
        # if "login" in request.url.path:
        #     return await call_next(request)
        #
        # if auth:
        #     token_data = token.verify_token(auth)
        #     if not isinstance(token_data, schemas.TokenData):
        #         return JSONResponse("Token Expired", 403)
        #     if request.method != "GET" and token_data.role_id == 3:
        #         return JSONResponse(
        #             "Not Authorization", 403, {"WWW-Authenticate": "Bearer"}
        #         )
        # else:
        #     return JSONResponse("Not Authorized", 403, {"WWW-Authenticate": "Bearer"})
        #
        # return response

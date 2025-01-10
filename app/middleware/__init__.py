import logging
from typing import Optional, Sequence

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette_context import request_cycle_context
from starlette_context.errors import ConfigurationError, MiddleWareValidationError
from starlette_context.plugins import Plugin

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

# https://stackoverflow.com/questions/64108406/fastapi-save-context-that-will-be-available-in-endpoints


class CustomContextMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        plugins: Optional[Sequence[Plugin]] = None,
        default_error_response: Response = Response(status_code=400),
        *args,
        **kwargs,
    ) -> None:
        super().__init__()
        for plugin in plugins or ():
            if not isinstance(plugin, Plugin):
                raise ConfigurationError(f"Plugin {plugin} is not valid instance")
        self.plugins = plugins or ()
        self.error_response = default_error_response

    async def set_context(self, request: Request) -> dict:
        """You might want to override this method.

        The dict it returns will be saved in the scope of a context. You
        can always do that later.
        """
        return {
            plugin.key: await plugin.process_request(request) for plugin in self.plugins
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            context = await self.set_context(request)
        except MiddleWareValidationError as e:
            error_response = e.error_response or self.error_response
            return error_response

        with request_cycle_context(context):
            # process rest of response stack
            response = await call_next(request)

            # gets back to middleware, process response with plugins
            for plugin in self.plugins:
                await plugin.enrich_response(response)
            # return response before resetting context
            # allowing further middlewares to still use the context
            return response
        # context reset


# def register_middleware(app: FastAPI):
#
#     @app.middleware("http")
#     async def custom_logging(request: Request, call_next):
#         start_time = time.time()
#
#         response = await call_next(request)
#         processing_time = time.time() - start_time
#         message = f"{request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"
#
#         print(message)
#         return response
#
#     @app.middleware("http")
#     async def authorization(request: Request, call_next):
#         if not "Authorization" in request.headers:
#             return JSONResponse(
#                 content={
#                     "message": "Not Authenticated",
#                     "resolution": "Please provide the right credentials to proceed",
#                 },
#                 status_code=401,
#             )
#         response = await call_next(request)
#
#         return response


# import base64
# import binascii
#
# from fastapi import Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from starlette.authentication import (
#     AuthCredentials,
#     AuthenticationBackend,
#     AuthenticationError,
#     SimpleUser,
# )
#
# from ..authorization import oauth2
# from ..databases import get_db
#
#
# class BasicAuthBackend(AuthenticationBackend):
#     async def authenticate(self, request, db: Session = Depends(get_db)):
#         if "Authorization" not in request.headers:
#             return
#
#         auth = request.headers["Authorization"]
#
#         try:
#             scheme, credentials = auth.split()
#             if scheme.lower() != "basic":
#                 return
#             decode = base64.b64decode(credentials).decode("ascii")
#         except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
#             raise AuthenticationError("Invalid basic auth credentials")
#
#         username, _, password = decode.partition(":")
#         user = oauth2.authenticate_user(username, password, db)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect username or password",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#
#         return AuthCredentials(["authenticated"]), SimpleUser(username)


# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.responses import JSONResponse
#
# from ..authorization.login import Token
#
#
# class AuthMiddleWare(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         if request.url.path in ["/docs", "/openapi.json"]:
#             return await call_next(request)
#
#         # 1. 토큰을 가져온다 (request.headers['Authorization']
#         auth_header = request.headers.get("Authorization")
#         print("auth_header:", auth_header)
#         # Bearer {TOKEN}
#         # 1-1 토큰이 없으면 status 403으로 반환
#         if not auth_header or not auth_header.startswith("Bearer"):
#             return JSONResponse(status_code=403, content={"status": 403})
#
#         token = auth_header.split(" ")[1]
#         print(token)
#
#         # 2. 토큰 검증
#         user_info = Token.verify_token(token)
#         print("user_info:", user_info)
#
#         # 2-1. 검증 실패 status 403 변환
#         if user_info is None:
#             return JSONResponse(status_code=403, content={"status": 403})
#
#         # 3. 유저 정보를 request 안에 user라는 키에 넣어준다
#         request.state.user = user_info
#
#         # 검증
#         # 1. route에서 request.status.user를 해서 값 가져옴
#         # 2. 로그인을 안한경우 status 403
#         response = await call_next(request)
#         return response

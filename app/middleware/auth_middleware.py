from fastapi.security import HTTPBearer
from starlette.authentication import AuthenticationBackend, AuthenticationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security
import threading

from starlette.responses import JSONResponse

from ..authorization import token
from jose import jwt, JWTError

# from fastapi_users.authentication import BearerTransport

# bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

thread_local = threading.local()


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if request.method == "GET" and path[1:] in [
            "docs",
            "openapi.json",
            "favicon.ico",
        ]:
            response = await call_next(request)  # Make sure `call_next` is not None
            return response

        response = await call_next(request)
        auth = response.headers.get("Authenticate")
        if "login" in path:
            if not auth:
                return JSONResponse(
                    "Incorrect username or password",
                    401,
                    {"WWW-Authenticate": "Bearer"},
                )
            token_type, access_token = auth.split(" ")
            return JSONResponse(
                content={"token_type": token_type, "access_token": access_token},
                headers={"WWW-Authenticate": "Bearer"},
            )
        response = await call_next(request)
        return response


class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        if not request.headers.get("Authenticate"):
            response = await call_next(request)
            return response

        response = await call_next(request)
        return response


#
# class AuthenticationMiddleware(AuthenticationBackend):
#     async def authenticate(self, request):
#         # This function is inherited from the base class and called by some other class
#         if "Authorization" not in request.headers:
#             return
#
#         auth = request.headers["Authorization"]
#         try:
#             scheme, token = auth.split()
#             if scheme.lower() != "bearer":
#                 return
#             decoded = jwt.decode(
#                 token,
#                 settings.JWT_SECRET,
#                 algorithms=[settings.JWT_ALGORITHM],
#                 options={"verify_aud": False},
#             )
#         except (ValueError, UnicodeDecodeError, JWTError) as exc:
#             raise AuthenticationError("Invalid JWT Token.")
#
#         username: str = decoded.get("sub")
#         token_data = TokenData(username=username)
#         # This is little hack rather making a generator function for get_db
#         db = LocalSession()
#         user = User.objects(db).filter(User.id == token_data.username).first()
#         # We must close the connection
#         db.close()
#         if user is None:
#             raise AuthenticationError("Invalid JWT Token.")
#         return auth, user


from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..authorization.token import decode_jwt


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid


#
# class AuthenticationMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next) -> Response:
#         auth = request.headers.get("Authorization")
#
#         if request.method == "GET" and request.url.path[1:] in [
#             "docs",
#             "openapi.json",
#             "favicon.ico",
#         ]:
#             # response = await call_next(request)  # Make sure `call_next` is not None
#             return await call_next(request)
#
#         # 처음 로그인
#         scheme, data = (auth or " ").split(" ", 1)
#         if scheme != "Basic":
#             return JSONResponse(None, 401, {"WWW-Authenticate": "Bearer"})
#         # username, password =
#         response = await call_next(request)
#         return response
#
#         # 다른 계정 로그인
#
#         # 다른 라우트


#
# class AuthorizationMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         # Before Authenticate
#         if "Authenticate" not in request.headers:
#             response = await call_next(request)
#             return response
#
#         # 처음 로그인 = auth 없고, login path
#         # 다른 로그인 = auth 있고, login path
#         # 다른 라우트 = auth 있고, login path 아님
#
#         if "login" in request.url.path:
#             response = await call_next(request)
#             # if response.headers.get("authorization"):
#             #     if hasattr(thread_local, "authorization"):
#             #         thread_local.authorization = None
#             #     thread_local.authorization = response.headers.get("Authorization")
#             return response
#
#         return await call_next(request)

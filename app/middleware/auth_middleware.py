from starlette.authentication import AuthenticationBackend, AuthenticationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security
import threading

from starlette.responses import JSONResponse

from ..authorization import token
from jose import jwt, JWTError

# from fastapi_users.authentication import BearerTransport

# bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

thread_local = threading.local()
# API_KEY = "your-secret-api-key"
# API_KEY_NAME = "access_token"
# api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class AuthenticationMiddleware(AuthenticationBackend):
    async def authenticate(self, request):

        # This function is inherited from the base class and called by some other class
        if hasattr(thread_local, "authorization"):
            return None

        # auth = request.headers["Authorization"]
        # try:
        #     scheme, data = auth.split()
        #     if scheme.lower() != "bearer":
        #         return
        #     decoded = jwt.decode(
        #         data,
        #         token.SECRET_KEY,
        #         algorithms=[token.ALGORITHM],
        #         options={"verify_aud": False},
        #     )
        # except (ValueError, UnicodeDecodeError, JWTError) as exc:
        #     raise AuthenticationError("Invalid JWT Token.")
        #
        # username: str = decoded.get("sub")
        # token_data = token.create_access_token(
        #     data={"sub": user.username, "role_id": user.role_id},
        #     expires_delta=access_token_expires,
        # )
        # # This is little hack rather making a generator function for get_db
        # db = LocalSession()
        # user = User.objects(db).filter(User.id == token_data.username).first()
        # # We must close the connection
        # db.close()
        # if user is None:
        #     raise AuthenticationError("Invalid JWT Token.")
        # return auth, user


class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if request.method == "GET" and path[1:] in [
            "docs",
            "openapi.json",
            "favicon.ico",
        ]:
            response = await call_next(request)  # Make sure `call_next` is not None
            return response
        # 처음 로그인 = auth 없고, login path
        # 다른 로그인 = auth 있고, login path
        # 다른 라우트 = auth 있고, login path 아님

        if "login" in path:
            response = await call_next(request)
            if response.headers.get("authorization"):
                if hasattr(thread_local, "authorization"):
                    thread_local.authorization = None
                thread_local.authorization = response.headers.get("Authorization")
            return response

        return await call_next(request)


# class AuthenticationMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         # Skip authentication for certain paths (like docs, openapi.json, favicon.ico)
#         path = request.url.path
#         if request.method == "GET" and path[1:] in [
#             "docs",
#             "openapi.json",
#             "favicon.ico",
#         ]:
#             return await call_next(request)
#
#         # Get the Authorization header from the request
#         auth = request.headers.get("Authorization")
#         scheme, data = (auth or " ").split(" ", 1)
#         if scheme != "Bearer":
#             return JSONResponse(None, 401, {"WWW-Authenticate": "Bearer"})
#
#         if auth and auth.startswith("Bearer "):
#             token = auth.split("Bearer ")[1]
#
#         response = await call_next(request)
#
#         return response


#
# if not auth:
#     return JSONResponse(
#         {
#             "detail": "Not authenticated. Please log in to access this resource.",
#             "login_url": "/login",  # Suggest login URL
#         },
#         status_code=401,
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#
# # Split the Authorization header into scheme and token
# try:
#     scheme, token = auth.split(" ")
# except ValueError:
#     return JSONResponse(
#         {"detail": "Invalid token format"},
#         status_code=401,
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#
# # Validate the scheme and token
# if scheme != "Bearer":
#     return JSONResponse(
#         {"detail": "Invalid authentication scheme"},
#         status_code=401,
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#
# # Validate the token (Assuming you have a method to verify the token)
# user = await oauth2.verify_token(token)
# if not user:
#     return JSONResponse(
#         {"detail": "Invalid or expired token"},
#         status_code=401,
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#
# # Store the user info in the request state for later use
# request.state.user = user
#
# # Call the next middleware or route handler
# response = await call_next(request)
# return response


#
# class AuthenticationMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#
#         # Authentication logic here
#         path = request.url.path
#         if request.method == "GET" and path[1:] in [
#             "docs",
#             "openapi.json",
#             "favicon.ico",
#         ]:
#             return await call_next(request)
#
#         # if "login" in path:
#         #     response: Response = await call_next(request)
#         auth = request.headers.get("Authorization")
#         if not auth:
#             return JSONResponse(
#                 {"detail": "Not authenticated"}, 401, {"WWW-Authenticate": "Bearer"}
#             )
#
#         response = await call_next(request)
#
#         scheme, data = (auth or " ").split(" ", 1)
#         request.state.authorization = data
#         request.headers.authorization = data
#
#         if scheme != "Bearer":
#             return JSONResponse(
#                 None,
#                 401,
#                 {"WWW-Authenticate": "Basic"},
#             )
#
#         response = await call_next(request)
#
#         return response


# class AuthorizationMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         user = request.headers.get("Authorization")
#         if user is None:
#             response = await call_next(request)
#             return response
#
#         user = getattr(request.state, "authorization")
#
#         path = request.url.path
#         # if "login" in path:
#         #     # Exception handle
#         #     return JSONResponse(
#         #         status_code=status.HTTP_400_BAD_REQUEST,
#         #         content={"detail": "Already authorized"},
#         #     )
#         user = request.headers.get("Authorization")
#         if not "Authorization" in request.headers:
#             response = await call_next(request)
#             response["Authorization"] = f"{request.user}"
#             # return JSONResponse(
#             #     status_code=status.HTTP_400_BAD_REQUEST,
#             #     content={"detail": "Unauthorized"},
#             # )
#         # Authorization logic here
#         user_role = request.user.role_id
#         if user_role not in [1, 2]:
#             return JSONResponse(status_code=403, content={"detail": "Forbidden"})
#
#         response = await call_next(request)
#         return response

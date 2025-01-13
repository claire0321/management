# https://m.blog.naver.com/indy9052/221934084260
from fastapi import FastAPI, HTTPException, Request
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    SimpleUser,
    AuthenticationError,
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse
import base64
import binascii


# Define the authentication backend (Basic Auth)
class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials")

        username, _, password = decoded.partition(":")
        # TODO: Verify the username and password, for now assume they're valid.
        return AuthCredentials(["authenticated"]), SimpleUser(username)


# Define the custom Authorization Middleware
class AuthorizationMiddleware:
    def __init__(self, app, allowed_roles: list):
        self.app = app
        self.allowed_roles = allowed_roles

    async def __call__(self, scope, receive, send):
        # Call the authentication middleware first
        await self.app(scope, receive, send)

        # After the authentication middleware, check the user's roles
        user = scope.get("user")
        if user and self.allowed_roles not in ["admin", "general", "manager"]:
            # If the user does not have the required role, reject the request
            response = PlainTextResponse("Forbidden", status_code=403)
            await response(scope, receive, send)
            return


# Create FastAPI application instance
app = FastAPI()


# Routes definition
@app.get("/")
async def homepage(request: Request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        return PlainTextResponse(f"Hello, {request.user.display_name}")
    return PlainTextResponse("Hello, you")


# Middleware configuration
middleware = [
    Middleware(
        AuthenticationMiddleware, backend=BasicAuthBackend()
    ),  # Add the Starlette AuthenticationMiddleware
    Middleware(
        AuthorizationMiddleware, allowed_roles="admin"
    ),  # Add the custom AuthorizationMiddleware
]

# Set up the app with both middlewares
app = FastAPI(middleware=middleware)


# ----------------------------------------------------------
# ------------- MIDDLEWARE UNDERSTANDING -------------------
# ----------------------------------------------------------

# from fastapi import FastAPI, APIRouter, Request, Response
# from fastapi.responses import JSONResponse
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.middleware.trustedhost import TrustedHostMiddleware
#
# app = FastAPI()
#
#
# # Define the custom middleware m1
# class MiddlewareM1(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         print("Middleware m1: before processing")
#         response = await call_next(request)
#         print("Middleware m1: after processing")
#         return response
#
#
# # Define the custom middleware m2
# class MiddlewareM2(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         print("Middleware m2: before processing")
#         response = await call_next(request)
#         print("Middleware m2: after processing")
#         return response
#
#
# # Create routers
# router1 = APIRouter()
# router2 = APIRouter()
#
#
# # Define route in router1
# @router1.get("/route1")
# async def route1():
#     print("Inside router 1")
#     return JSONResponse(content={"message": "Response from route 1"})
#
#
# # Define route in router2
# @router2.get("/route2")
# async def route2():
#     print("Inside router 2")
#     return JSONResponse(content={"message": "Response from route 2"})
#
#
# # Add the routers to the app
# app.include_router(router1)
# app.include_router(router2)
#
# # Apply middlewares to the app
# app.add_middleware(MiddlewareM1)
# app.add_middleware(MiddlewareM2)

# --------------------------------------------------------------------
# -------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
#
# from fastapi import FastAPI, Depends, HTTPException, Security
# from fastapi.security.api_key import APIKeyHeader
# from .authorization.token import SECRET_KEY
#
# app = FastAPI()
#
# API_KEY = "your-secret-api-key"
# API_KEY_NAME = "access_token"
# api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
#
#
# def get_api_key(api_key_header: str = Security(api_key_header)):
#     if api_key_header == SECRET_KEY:
#         return api_key_header
#     else:
#         raise HTTPException(status_code=403, detail="Could not validate credentials")
#
#
# @app.get("/protected-route")
# async def protected_route(api_key: str = Depends(get_api_key)):
#     return {"message": "You have access to this route"}
#
#
# @app.get("/unprotected-route")
# async def unprotected_route():
#     return {"message": "This route is open to everyone"}


# from starlette.applications import Starlette
# from starlette.authentication import (
#     AuthCredentials,
#     AuthenticationBackend,
#     AuthenticationError,
#     SimpleUser,
# )
# from starlette.middleware import Middleware
# from starlette.middleware.authentication import AuthenticationMiddleware
# from starlette.responses import PlainTextResponse
# from starlette.routing import Route
# import base64
# import binascii
#
#
# class BasicAuthBackend(AuthenticationBackend):
#     async def authenticate(self, conn):
#         if "Authorization" not in conn.headers:
#             return
#
#         auth = conn.headers["Authorization"]
#         try:
#             scheme, credentials = auth.split()
#             if scheme.lower() != "basic":
#                 return
#             decoded = base64.b64decode(credentials).decode("ascii")
#         except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
#             raise AuthenticationError("Invalid basic auth credentials")
#
#         username, _, password = decoded.partition(":")
#         # TODO: You'd want to verify the username and password here.
#         return AuthCredentials(["authenticated"]), SimpleUser(username)
#
#
# async def homepage(request):
#     if request.user.is_authenticated:
#         return PlainTextResponse("Hello, " + request.user.display_name)
#     return PlainTextResponse("Hello, you")
#
#
# routes = [Route("/", endpoint=homepage)]
#
# middleware = [Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())]
#
# app = Starlette(routes=routes, middleware=middleware)

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------


# from typing import Callable
#
# import jwt  # You can use any JWT library
# from fastapi import FastAPI, HTTPException
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.requests import Request
#
# SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
#
#
# class BearerAuthMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next: Callable):
#         authorization: str = request.headers.get("Authorization")
#
#         # Check if the Authorization header is present and starts with "Bearer "
#         if authorization and authorization.startswith("Bearer "):
#             token = authorization.split("Bearer ")[1]
#             try:
#                 # Verify the token (you should use your preferred method of validation)
#                 decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#                 # You can attach the decoded token to the request if needed
#                 request.state.user = (
#                     decoded_token  # Attach the user data to request state
#                 )
#             except jwt.PyJWTError:
#                 raise HTTPException(status_code=401, detail="Invalid or expired token")
#
#         # Proceed with the request
#         response = await call_next(request)
#         return response
#
#
# # Initialize FastAPI application
# app = FastAPI()
#
# # Add the BearerAuthMiddleware to the app
# app.add_middleware(BearerAuthMiddleware)
#
#
# @app.get("/secure-endpoint")
# async def secure_endpoint(request: Request):
#     # If the middleware is successful, you can access user info from request.state
#     if hasattr(request.state, "user"):
#         return {"message": "Access granted", "user": request.state.user}
#     else:
#         raise HTTPException(status_code=401, detail="Unauthorized")


# import logging
#
# from fastapi import FastAPI
# from starlette.requests import Request
# from starlette_context import context
# from starlette_context.middleware import ContextMiddleware
#
# app = FastAPI(title="TestAPI", description="This is test API project", version="0.0.1")
#
#
# async def audit_log(request: Request, call_next):
#     response = await call_next(request)
#     if "user_id" in context:
#         logging.info("user id : {}".format(context["user_id"]))
#     if "user_name" in context:
#         logging.info("user name : {}".format(context["user_name"]))
#
#     return response
#
#
# app.middleware("http")(audit_log)
# app.add_middleware(ContextMiddleware)
#
#
# @app.get("/")
# def get_root(id: str, name: str):
#     context.update(user_id=id)
#     context.update(user_name=name)
#     return {"Hello": "World"}


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------

# import base64
#
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
#
# app = FastAPI()
#
#
# @app.middleware("http")
# async def check_authentication(request: Request, call_next):
#     auth = request.headers.get("Authorization")
#     # The following paths are always allowed:
#     if request.method == "GET" and request.url.path[1:] in [
#         "docs",
#         "openapi.json",
#         "favicon.ico",
#     ]:
#         return await call_next(request)
#     # Parse auth header and check scheme, username and password
#     scheme, data = (auth or " ").split(" ", 1)
#     if scheme != "Basic":
#         return JSONResponse(None, 401, {"WWW-Authenticate": "Basic"})
#     username, password = base64.b64decode(data).decode().split(":", 1)
#     if username == "john" and password == "test123":
#         return await call_next(request)
#
#
# @app.get("/test")
# async def root():
#     return {"message": "Hello World"}


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------

# import jwt
# from fastapi import FastAPI, Request, HTTPException
# from starlette.middleware.base import BaseHTTPMiddleware
#
# # 비밀키와 알고리즘
# SECRET_KEY = "your_secret_key"
# ALGORITHM = "HS256"
#
#
# # Context Middleware
# class ContextMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         # Context 정보 설정
#         request.state.user = {
#             "user_id": 1,
#             "username": "test_user",
#             "role": "admin",
#         }  # 예시 사용자
#         request.state.db = "fake_database_connection"  # 예시 DB 연결 객체
#
#         # 요청을 처리하고 응답을 받음
#         response = await call_next(request)
#         return response
#
#
# # Authentication and Authorization Middleware
# class AuthMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         # Authorization 헤더에서 토큰을 추출
#         authorization: str = request.headers.get("Authorization")
#
#         if not authorization:
#             return HTTPException(
#                 status_code=401, detail="Authorization token is missing"
#             )
#
#         token = authorization.split(" ")[1]  # "Bearer <token>" 형식에서 토큰 추출
#
#         try:
#             # JWT 토큰 검증
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             request.state.user = payload  # 사용자 정보를 request state에 저장
#         except jwt.ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="Token has expired")
#         except jwt.InvalidTokenError:
#             raise HTTPException(status_code=401, detail="Invalid token")
#
#         # 권한 검사
#         if request.state.user.get("role") != "admin":
#             raise HTTPException(
#                 status_code=403, detail="Forbidden: You don't have permission"
#             )
#
#         # 인증과 권한 확인 후 요청을 처리
#         response = await call_next(request)
#         return response
#
#
# # FastAPI 애플리케이션 설정
# app = FastAPI()
#
# # 미들웨어 추가
# app.add_middleware(ContextMiddleware)
# app.add_middleware(AuthMiddleware)
#
#
# # 테스트용 엔드포인트
# @app.get("/context")
# async def get_context(request: Request):
#     user = request.state.user
#     db = request.state.db
#     return {"user": user, "db": db}
#
#
# @app.get("/protected")
# async def protected_route(request: Request):
#     user = request.state.user
#     return {"message": f"Hello {user['username']}, you are authorized!"}
#
#
# @app.get("/public")
# async def public_route():
#     return {"message": "This is a public route!"}


#
# from datetime import datetime, timedelta
#
#
# # Function to create a JWT token
# def create_access_token(username: str):
#     expiration = timedelta(hours=1)
#     to_encode = {"sub": username, "exp": datetime.utcnow() + expiration}
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
#
# # Example: creating a token for user1
# token = create_access_token("user1")
# print(token)  # Store this token in the client side
#
#
# @app.get("/user-data")
# async def get_user_data(user: dict = Depends(get_current_user)):
#     return {"message": f"Hello, {user['username']}! Your role is {user['role']}."}

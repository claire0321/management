import base64

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


def check_permission(method, api, auth):
    # The following paths are always allowed:
    if method == "GET" and api[1:] in ["docs", "openapi.json", "favicon.ico"]:
        return True
    # Parse auth header and check scheme, username and password
    scheme, data = (auth or " ").split(" ", 1)
    if scheme != "Basic":
        return False
    username, password = base64.b64decode(data).decode().split(":", 1)
    if username == "john" and password == "test123":
        return True


@app.middleware("http")
async def check_authentication(request: Request, call_next):
    auth = request.headers.get("Authorization")
    if not check_permission(request.method, request.url.path, auth):
        return JSONResponse(None, 401, {"WWW-Authenticate": "Basic"})
    return await call_next(request)


@app.get("/test")
async def root():
    return {"message": "Hello World"}


# from fastapi import FastAPI, Request, HTTPException, Depends
# from jose import JWTError, jwt
# from starlette.middleware.base import BaseHTTPMiddleware
#
# # Secret key for JWT encoding and decoding
# SECRET_KEY = "your_secret_key"
# ALGORITHM = "HS256"
#
# # Your user model (can be replaced with an actual DB call or ORM)
# users_db = {
#     "user1": {"username": "user1", "role": "admin"},
#     "user2": {"username": "user2", "role": "editor"},
# }
#
#
# class AuthenticationMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         authorization: str = request.headers.get("Authorization")
#         if authorization is None:
#             raise HTTPException(status_code=401, detail="Authorization header missing")
#
#         try:
#             token = authorization.split(" ")[1]
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             username: str = payload.get("sub")
#             if username is None:
#                 raise HTTPException(status_code=401, detail="Token has no sub")
#
#             request.state.username = username
#         except JWTError:
#             raise HTTPException(status_code=401, detail="Invalid token")
#
#         response = await call_next(request)
#         return response
#
#
# app = FastAPI()
#
# # app.add_middleware(AuthenticationMiddleware)
#
#
# # Custom dependency to check the role
# def get_current_user(request: Request):
#     username = request.state.username
#     if username not in users_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     return users_db[username]
#
#
# def require_role(role: str):
#     def role_dependency(user: dict = Depends(get_current_user)):
#         if user["role"] != role:
#             raise HTTPException(status_code=403, detail="Not authorized")
#         return user
#
#     return role_dependency
#
#
# # Example of a route that requires admin role
# @app.get("/admin-data")
# async def get_admin_data(user: dict = Depends(require_role("admin"))):
#     return {"message": f"Welcome, {user['username']}! You have admin access."}
#
#
# # Example of a route that requires editor role
# @app.get("/editor-data")
# async def get_editor_data(user: dict = Depends(require_role("editor"))):
#     return {"message": f"Welcome, {user['username']}! You have editor access."}
#
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

# https://www.youtube.com/watch?v=ZX4I6xginvc
# https://www.youtube.com/watch?v=-AM5QVkb0OM
from fastapi import FastAPI

from . import models
from .databases import engine
from .middleware import auth_middleware
from .routers import authentication, users, roles
from starlette.middleware.authentication import AuthenticationMiddleware

app = FastAPI()


# register_middleware(app)

models.Base.metadata.create_all(bind=engine)

app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(roles.router)

# app.add_middleware(ContextMiddleware)
# app.add_middleware(
#     AuthenticationMiddleware, backend=auth_middleware.AuthenticationMiddleware()
# )
app.add_middleware(auth_middleware.AuthenticationMiddleware)
app.add_middleware(auth_middleware.AuthorizationMiddleware)


# app.add_middleware(
#     CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
# )
# app.add_middleware(log.AuthenticationMiddleware)
# app.add_middleware(log.AuthorizationMiddleware)
# app.add_middleware(log.ContextSetMiddleware)
# app.add_middleware(log.SQLAlchemyMiddleware)
# app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
# app.add_middleware(log.LoggingRequestMiddleware)
# app.add_middleware(log.TimeHeaderLoggerSetMiddleware)

#
# from starlette.middleware.base import BaseHTTPMiddleware
#
#
# # class MyMiddleware(BaseHTTPMiddleware):
# #     async def dispatch(self, request, call_next):
# #         start_time = time.time()
# #         response = await call_next(request)
# #         process_time = time.time() - start_time
# #         response.headers["X-Process-Time"] = str(process_time)
# #         return response
#
#
# class CustomMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         print("Before processing the request")
#
#         response = await call_next(request)
#
#         print("After processing the request")
#
#         return response
#
#
# app.add_middleware(CustomMiddleware)
#
#
# # origins = ["http://localhost:8000", "http://localhost:3000"]
# # app.add_middleware(MyMiddleware)
# # # app.add_middleware(CORSMiddleware, allow_origins=origins)
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=origins,
# #     allow_credentials=True,
# #     allow_methods=["*"],
# # )
#
#
# @app.get("/blah")
# async def blah():
#     return {"hello": "world"}
#

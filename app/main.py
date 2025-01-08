# https://www.youtube.com/watch?v=ZX4I6xginvc
# https://www.youtube.com/watch?v=-AM5QVkb0OM
from fastapi import FastAPI

from . import models
from .databases import engine
from .routers import authentication, users, roles

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(roles.router)

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

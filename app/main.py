from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import initialize_data
from app.databases.database import engine, Base
from app.error import exception_handler
from app.middleware import init_middleware
from app.redis import redis_cache
from app.routers import authentication, users, roles


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_data()
    yield


app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
def shutdown_event():
    redis_cache.flushdb()


#
#
# @app.get("/test2")
# async def test2():
#     rd = await redis_test2()
#
#     return {"res": rd}


def init_router():
    app.include_router(authentication.router)
    app.include_router(users.router)
    app.include_router(roles.router)


def create_app():
    init_router()
    init_middleware(app)
    exception_handler(app)


create_app()

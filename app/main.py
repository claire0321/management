from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from app import initialize_data
from app.databases.database import engine, Base
from app.databases.redis_base import redis_connect, redis_disconnect, redis_rd
from app.error import exception_handler
from app.middleware import init_middleware
from app.routers import authentication, users, roles


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_data()
    redis_connect()
    yield
    redis_disconnect()


app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)

redis_test = APIRouter(
    prefix="/redis",
    tags=["Redis"]
)


@redis_test.get("/get-redis")
async def show_redis():
    return redis_rd()


@redis_test.put("/delete")
async def delete_redis():
    redis_rd().flushdb()
    return {"message": "Cache removed"}


def init_router():
    app.include_router(authentication.router)
    app.include_router(users.router)
    app.include_router(roles.router)
    app.include_router(redis_test)


def create_app():
    init_router()
    init_middleware(app)
    exception_handler(app)


create_app()

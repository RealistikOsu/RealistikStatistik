from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi import Request
from shared_modules import logger

from app.common import settings
from app.common import statsd
from app.services import database
from app.services import redis


def init_db(api: FastAPI) -> None:
    @api.on_event("startup")
    async def startup_db() -> None:
        logger.info("Starting up database pool")
        database_service = database.Database(
            read_dsn="mysql+asyncmy://{username}:{password}@{host}:{port}/{db}".format(
                username=settings.READ_DB_USER,
                password=settings.READ_DB_PASS,
                host=settings.READ_DB_HOST,
                port=settings.READ_DB_PORT,
                db=settings.READ_DB_NAME,
            ),
            write_dsn="mysql+asyncmy://{username}:{password}@{host}:{port}/{db}".format(
                username=settings.WRITE_DB_USER,
                password=settings.WRITE_DB_PASS,
                host=settings.WRITE_DB_HOST,
                port=settings.WRITE_DB_PORT,
                db=settings.WRITE_DB_NAME,
            ),
        )
        await database_service.connect()
        api.state.db = database_service
        logger.info("Database pool started up")

    @api.on_event("shutdown")
    async def shutdown_db() -> None:
        logger.info("Shutting down database pool")
        await api.state.db.disconnect()
        del api.state.db
        logger.info("Database pool shut down")


def init_redis(api: FastAPI) -> None:
    @api.on_event("startup")
    async def startup_redis() -> None:
        logger.info("Starting up redis pool")
        service_redis = redis.ServiceRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
        )
        await service_redis.initialize()
        api.state.redis = service_redis
        logger.info("Redis pool started up")

    @api.on_event("shutdown")
    async def shutdown_redis() -> None:
        logger.info("Shutting down the redis")
        await api.state.redis.close()
        del api.state.redis
        logger.info("Redis pool shut down")


def init_middlewares(api: FastAPI) -> None:
    @api.middleware("http")
    async def add_db_to_request(request: Request, call_next):
        request.state.db = request.app.state.db
        response = await call_next(request)
        return response

    @api.middleware("http")
    async def add_redis_to_request(request: Request, call_next):
        request.state.redis = request.app.state.redis
        response = await call_next(request)
        return response

    @api.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter_ns()
        response = await call_next(request)
        process_time = (time.perf_counter_ns() - start_time) / 1e6
        response.headers["X-Process-Time"] = str(process_time)  # ms

        route = request.scope.get("route")
        statsd.timing(
            "statistics.request.time",
            process_time,
            [
                f"route:{route.path if route else 'unmatched'}",
                f"status:{response.status_code // 100}xx",
            ],
        )
        return response


def init_routes(api: FastAPI) -> None:
    from .v1 import router as v1_router

    api.include_router(v1_router)


def init_api():
    api = FastAPI()

    init_db(api)
    init_redis(api)
    init_middlewares(api)
    init_routes(api)
    return api

#!/usr/bin/env python3.10
# To run it you need to:
# `cd path/to/profile-history-service && venv/bin/python -m app.workers.daemons.online_history_crawler`
from __future__ import annotations

import asyncio
from timeit import default_timer as timer

from shared_modules import logger

from app.common import settings
from app.services import redis as redis_service

REDIS_HISTORY_KEY = "statistik:online:history"
MAX_HISTORY_SIZE = 288  # every 5 minutes.


async def update_online_history() -> None:

    current_count = await redis.get("ripple:online_users")

    if current_count is None:
        current_count = 0
    else:
        current_count = int(current_count)

    list_size = await redis.llen(REDIS_HISTORY_KEY)

    if list_size >= MAX_HISTORY_SIZE:
        await redis.lpop(REDIS_HISTORY_KEY)

    await redis.rpush(REDIS_HISTORY_KEY, current_count)


async def async_main() -> int:
    global redis, db

    redis = await redis_service.ServiceRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )
    await redis.initialize()

    while True:
        start = timer()
        await update_online_history()
        end = timer()

        logger.info(f"[online_history_crawler:cron] Time taken: {end - start:.2f}s")

        await asyncio.sleep(5 * 60)

    await redis.close()
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(async_main())
    raise SystemExit(exit_code)

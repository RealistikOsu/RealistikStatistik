#!/usr/bin/env python3.10
# To run it you need to:
# `cd path/to/profile-history-service && venv/bin/python -m app.workers.daemons.top_scores_crawler`
from __future__ import annotations

import asyncio
from timeit import default_timer as timer

import orjson
from shared_modules import logger

from app.common import settings
from app.services import database
from app.services import redis as redis_service

redis_map = {
    0: ("vn", "std"),
    1: ("vn", "taiko"),
    2: ("vn", "ctb"),
    3: ("vn", "mania"),
    4: ("rx", "std"),
    5: ("rx", "taiko"),
    6: ("rx", "ctb"),
    7: ("ap", "std"),
}

# Clean schema: single `scores` table keyed by combined mode 0-7; the row keys
# below are preserved via `AS` aliases so the cached redis payload is unchanged.

REDIS_KEY_TEMPLATE = "statistik:cache:top:{}:{}"


async def gather_profile_history() -> None:

    for mode in range(8):
        (c_mode_name, mode_name) = redis_map[mode]

        score_data = await db.fetch_one(
            """
                SELECT CONVERT(`s`.`pp`, SIGNED) AS `pp_val`, `u`.`username`,
                       `u`.`id` AS `user_id`, UNIX_TIMESTAMP(`s`.`submitted_at`) AS `time`,
                       `b`.`id` AS `beatmap_id`, `b`.`set_id` AS `beatmapset_id`
                FROM `scores` `s`
                INNER JOIN `users` `u` ON `s`.`user_id` = `u`.`id`
                INNER JOIN `beatmaps` `b` ON `s`.`beatmap_md5` = `b`.`md5`
                WHERE `s`.`mode` = :mode AND `s`.`status` = 3
                AND `u`.`public` = 1 AND `b`.`status` IN (2, 3)
                ORDER BY `s`.`pp` DESC LIMIT 1
            """,
            {
                "mode": mode,
            },
        )

        if score_data is None:
            continue

        redis_key = REDIS_KEY_TEMPLATE.format(c_mode_name, mode_name)
        await redis.set(redis_key, orjson.dumps(dict(score_data)))


async def async_main() -> int:
    global redis, db

    redis = await redis_service.ServiceRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    )
    await redis.initialize()
    db = database.Database(
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
    await db.connect()

    start = timer()
    await gather_profile_history()
    end = timer()

    logger.info(f"[top_scores_crawler:cron] Time taken: {end - start:.2f}s")
    await db.disconnect()
    await redis.close()
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(async_main())
    raise SystemExit(exit_code)

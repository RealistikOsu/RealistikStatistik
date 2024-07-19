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

db_map = {
    0: ("scores", 0),
    1: ("scores", 1),
    2: ("scores", 2),
    3: ("scores", 3),
    4: ("scores_relax", 0),
    5: ("scores_relax", 1),
    6: ("scores_relax", 2),
    7: ("scores_ap", 0),
}

REDIS_KEY_TEMPLATE = "statistik:cache:top:{}:{}"


async def gather_profile_history() -> None:

    for mode in range(8):
        (db_table, mode_val) = db_map[mode]
        (c_mode_name, mode_name) = redis_map[mode]

        score_data = await db.fetch_one(
            f"""
                SELECT CONVERT(`s`.`pp`, SIGNED) AS `pp_val`, `u`.`username`, `u`.`id` AS `user_id`, `s`.`time`, `b`.`beatmap_id`, `b`.`beatmapset_id`
                FROM `{db_table}` `s` INNER JOIN `users` `u` INNER JOIN `beatmaps` `b`
                ON `s`.`userid` = `u`.`id` AND `s`.`beatmap_md5` = `b`.`beatmap_md5`
                WHERE `s`.`play_mode` = :mode_val
                AND `s`.`completed` = 3 AND `u`.`privileges` & 1
                AND `b`.`ranked` IN (2,3)
                ORDER BY `s`.`pp` DESC LIMIT 1
            """,
            {
                "mode_val": mode_val,
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

    while True:
        start = timer()
        await gather_profile_history()
        end = timer()

        logger.info(f"[top_scores_crawler:cron] Time taken: {end - start:.2f}s")
        await asyncio.sleep(5 * 60)

    await db.disconnect()
    await redis.close()
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(async_main())
    raise SystemExit(exit_code)

from __future__ import annotations

import datetime

from app.common.context import Context
from app.models.c_rank import CountryRankCapture
from app.models.c_rank import CountryRankHistory
from app.repositories.c_rank import CountryRanksRepo

mode_map = {
    0: ("leaderboard", "std"),
    1: ("leaderboard", "taiko"),
    2: ("leaderboard", "ctb"),
    3: ("leaderboard", "mania"),
    4: ("relaxboard", "std"),
    5: ("relaxboard", "taiko"),
    6: ("relaxboard", "ctb"),
    7: ("autoboard", "std"),
}


async def fetch_many(
    ctx: Context,
    user_id: int,
    mode: int,
    limit: int = 89,  # one will be added in api.
) -> CountryRankHistory:
    r_repo = CountryRanksRepo(ctx)
    resp = await r_repo.fetch_many(user_id, mode, limit)

    data_structure = {"user_id": user_id, "mode": mode, "captures": resp}
    return CountryRankHistory.from_mapping(data_structure)


async def fetch_current(
    ctx: Context,
    user_id: int,
    mode: int,
    country: str,
) -> CountryRankCapture | None:

    (redis_key, mode_name) = mode_map[mode]
    current_rank = await ctx.redis.zrevrank(
        f"ripple:{redis_key}:{mode_name}:{country.lower()}",
        user_id,
    )

    if current_rank is None:
        return None

    current_rank_captured_at = datetime.datetime.now()
    data_structure = {
        "captured_at": current_rank_captured_at,
        "c_rank": current_rank + 1,  # 0-indexed.
    }

    return CountryRankCapture.from_mapping(data_structure)

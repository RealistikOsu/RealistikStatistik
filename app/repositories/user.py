from __future__ import annotations

from typing import Any
from typing import Mapping

from app.common.context import Context


class UsersRepo:

    READ_PARAMS = """\
        `privileges`, `public`, `country`, COALESCE(UNIX_TIMESTAMP(`latest_activity`),0) AS `latest_activity`
    """

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    async def fetch_one(
        self,
        user_id: int,
    ) -> Mapping[str, Any] | None:

        query = f"""\
            SELECT {self.READ_PARAMS}
              FROM `users`
             WHERE `id` = :user_id LIMIT 1
        """
        params = {
            "user_id": user_id,
        }
        return await self.ctx.db.fetch_one(query, params)

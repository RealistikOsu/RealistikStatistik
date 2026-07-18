from __future__ import annotations

import time


def is_restricted(public: int) -> bool:
    # Bans/restrictions live in the `users.public` cache in the clean schema
    # (privileges bit 1 is now ACTIVATED, not the old UserPublic).
    return not public


def is_not_active(last_active: int) -> bool:

    delta_time = int(time.time()) - last_active
    days = delta_time / 60 / 60 / 24
    return days > 60

from __future__ import annotations

from typing import Any
from typing import Mapping

from pydantic import BaseModel


class UserInfo(BaseModel):
    privileges: int
    public: int
    country: str
    latest_activity: int

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> UserInfo:
        return cls(
            privileges=mapping["privileges"],
            public=mapping["public"],
            country=mapping["country"],
            latest_activity=mapping["latest_activity"],
        )

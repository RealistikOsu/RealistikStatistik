from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends

from app.api.rest.context import RequestContext
from app.common import responses
from app.common.errors import ServiceError
from app.common.responses import Success
from app.models.pp import PPHistory
from app.usecases import pp
from app.usecases import user
from app.usecases import validation

router = APIRouter()


@router.get("/profile-history/pp", response_model=Success[PPHistory])
async def get_profile_pp_history(
    user_id: int,
    mode: int,
    ctx: RequestContext = Depends(),
):
    data = await pp.fetch_many(ctx, user_id, mode)
    user_data = await user.fetch_one(ctx, user_id)

    if isinstance(user_data, ServiceError):
        return responses.failure(
            user_data,
            "Failed to fetch user data.",
            status_code=200,
        )

    if validation.is_restricted(user_data.public):
        return responses.failure(
            ServiceError.USERS_IS_RESTRICTED,
            "User is restricted.",
            status_code=200,
        )

    if validation.is_not_active(user_data.latest_activity):
        return responses.failure(
            ServiceError.USERS_IS_NOT_ACTIVE,
            "User is not active.",
            status_code=200,
        )

    # get current pp to create in real time pp history.
    current_pp_capture = await pp.fetch_current(ctx, user_id, mode)

    if not current_pp_capture:
        return responses.failure(
            ServiceError.PP_NOT_FOUND,
            "Failed to fetch newest pp capture.",
            status_code=200,
        )

    data.captures.append(current_pp_capture)
    return responses.success(data)

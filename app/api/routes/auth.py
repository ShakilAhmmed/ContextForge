from fastapi import APIRouter, Depends, status

from app.controllers import auth_controller
from app.core.rate_limit import rate_limit
from app.schemas.auth import TokenData, UserRead
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/auth", tags=["auth"])

router.add_api_route(
    "/register",
    auth_controller.register,
    methods=["POST"],
    response_model=SuccessResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/login",
    auth_controller.login,
    methods=["POST"],
    response_model=SuccessResponse[TokenData],
    dependencies=[Depends(rate_limit("login", "rate_limit_login", "rate_limit_login_window_seconds"))],
)
router.add_api_route(
    "/me",
    auth_controller.me,
    methods=["GET"],
    response_model=SuccessResponse[UserRead],
)

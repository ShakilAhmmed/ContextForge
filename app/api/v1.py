from fastapi import APIRouter, Depends

from app.api.routes.auth import router as auth_router
from app.api.routes.tenants import router as tenants_router
from app.core.rate_limit import rate_limit

router = APIRouter(
    prefix="/api/v1",
    dependencies=[
        Depends(rate_limit("default", "rate_limit_default", "rate_limit_default_window_seconds"))
    ],
)
router.include_router(tenants_router)
router.include_router(auth_router)

from fastapi import APIRouter, Depends

from app.controllers.auth_controller import router as auth_router
from app.controllers.chat_controller import router as chat_router
from app.controllers.document_controller import router as documents_router
from app.controllers.tenant_controller import router as tenants_router
from app.core.rate_limit import rate_limit

router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(rate_limit("default", "rate_limit_default", "rate_limit_default_window_seconds"))],
)
router.include_router(tenants_router)
router.include_router(auth_router)
router.include_router(documents_router)
router.include_router(chat_router)

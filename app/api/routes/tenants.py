from fastapi import APIRouter, status

from app.controllers import tenant_controller
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.tenant import TenantRead

router = APIRouter(prefix="/tenants", tags=["tenants"])

router.add_api_route(
    "",
    tenant_controller.create_tenant,
    methods=["POST"],
    response_model=SuccessResponse[TenantRead],
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "",
    tenant_controller.list_tenants,
    methods=["GET"],
    response_model=PaginatedResponse[TenantRead],
)
router.add_api_route(
    "/{tenant_id}",
    tenant_controller.get_tenant,
    methods=["GET"],
    response_model=SuccessResponse[TenantRead],
)

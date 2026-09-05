from fastapi import APIRouter, status

from app.controllers import document_controller
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.document import DocumentRead

router = APIRouter(prefix="/documents", tags=["documents"])

router.add_api_route(
    "",
    document_controller.upload_document,
    methods=["POST"],
    response_model=SuccessResponse[DocumentRead],
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "",
    document_controller.list_documents,
    methods=["GET"],
    response_model=PaginatedResponse[DocumentRead],
)
router.add_api_route(
    "/{document_id}",
    document_controller.get_document,
    methods=["GET"],
    response_model=SuccessResponse[DocumentRead],
)

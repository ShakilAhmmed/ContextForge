from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorBody, ErrorDetail, ErrorResponse

_TYPE_BY_STATUS = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict) and "type" in detail and "message" in detail:
            error_type, message = detail["type"], detail["message"]
        else:
            error_type = _TYPE_BY_STATUS.get(exc.status_code, "error")
            message = detail if isinstance(detail, str) else error_type
        body = ErrorResponse(code=exc.status_code, error=ErrorBody(type=error_type, message=message))
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            ErrorDetail(field=".".join(str(p) for p in err["loc"][1:]) or None, message=err["msg"])
            for err in exc.errors()
        ]
        body = ErrorResponse(
            code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            error=ErrorBody(type="validation_error", message="request validation failed", details=details),
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=body.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        body = ErrorResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=ErrorBody(type="internal_error", message="internal server error"),
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body.model_dump())

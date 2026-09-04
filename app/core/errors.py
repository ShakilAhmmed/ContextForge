from fastapi import HTTPException, status


class ApiError(HTTPException):
    """HTTPException carrying a stable machine-readable `type`, so the global
    handler can render the standard error contract without guessing from
    the status code."""

    def __init__(self, status_code: int, error_type: str, message: str) -> None:
        super().__init__(status_code=status_code, detail={"type": error_type, "message": message})


def not_found(message: str) -> ApiError:
    return ApiError(status.HTTP_404_NOT_FOUND, "not_found", message)


def conflict(message: str) -> ApiError:
    return ApiError(status.HTTP_409_CONFLICT, "conflict", message)

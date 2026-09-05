from fastapi import HTTPException, status


class ApiError(HTTPException):
    """HTTPException carrying a stable machine-readable `type`, so the global
    handler can render the standard error contract without guessing from
    the status code."""

    def __init__(
        self, status_code: int, error_type: str, message: str, headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(
            status_code=status_code, detail={"type": error_type, "message": message}, headers=headers
        )


def not_found(message: str) -> ApiError:
    return ApiError(status.HTTP_404_NOT_FOUND, "not_found", message)


def conflict(message: str) -> ApiError:
    return ApiError(status.HTTP_409_CONFLICT, "conflict", message)


def unauthorized(message: str) -> ApiError:
    return ApiError(status.HTTP_401_UNAUTHORIZED, "unauthorized", message)


def forbidden(message: str) -> ApiError:
    return ApiError(status.HTTP_403_FORBIDDEN, "forbidden", message)


def bad_request(message: str) -> ApiError:
    return ApiError(status.HTTP_400_BAD_REQUEST, "bad_request", message)


def payload_too_large(message: str) -> ApiError:
    return ApiError(status.HTTP_413_CONTENT_TOO_LARGE, "payload_too_large", message)


def rate_limited(message: str, retry_after_seconds: int) -> ApiError:
    return ApiError(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "rate_limited",
        message,
        headers={"Retry-After": str(retry_after_seconds)},
    )

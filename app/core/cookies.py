from fastapi import Response

from app.core.config import settings


def set_auth_cookies(response: Response, access_token: str, expires_in: int) -> None:
    response.set_cookie(
        key=settings.access_token_cookie_name,
        value=access_token,
        max_age=expires_in,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="none",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key=settings.access_token_cookie_name, path="/", samesite="none")

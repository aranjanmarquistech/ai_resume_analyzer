from __future__ import annotations

from fastapi import HTTPException, status


def bad_request(msg: str, detail: str | None = None) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": msg, "detail": detail},
    )


def unauthorized(msg: str = "Unauthorized") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": msg, "detail": "Missing or invalid API key"},
    )


def too_large(msg: str = "File too large", detail: str | None = None) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail={"error": msg, "detail": detail},
    )

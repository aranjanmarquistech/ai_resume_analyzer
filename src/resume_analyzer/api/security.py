from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from resume_analyzer.api.config import settings

api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Security(api_key_scheme)) -> None:
    expected = (settings.RESUME_API_KEY or "").strip()

    # dev mode: if not set -> allow
    if not expected:
        return

    if not api_key or api_key.strip() != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

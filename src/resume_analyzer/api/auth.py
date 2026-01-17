from __future__ import annotations

from fastapi import Header

from .config import settings
from .errors import unauthorized


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    # If you also want Authorization later, we can add it. For now keep it simple.
    print("RECEIVED:", repr(x_api_key))
    print("EXPECTED:", repr(settings.RESUME_API_KEY))
    print("EQUAL:", x_api_key == settings.RESUME_API_KEY)

    if not x_api_key or x_api_key != settings.RESUME_API_KEY:

        raise unauthorized()
    return x_api_key

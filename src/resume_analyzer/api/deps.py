from __future__ import annotations

from fastapi import UploadFile

from .config import settings
from .errors import bad_request, too_large


ALLOWED_RESUME_EXT = {".pdf", ".docx"}
ALLOWED_JD_EXT = {".txt", ".pdf", ".docx"}


def _ext(filename: str) -> str:
    filename = filename.lower().strip()
    dot = filename.rfind(".")
    return filename[dot:] if dot != -1 else ""


async def validate_upload(file: UploadFile, allowed_ext: set[str], kind: str) -> bytes:
    if not file.filename:
        raise bad_request(f"{kind} missing", f"No filename provided for {kind}")

    ext = _ext(file.filename)
    if ext not in allowed_ext:
        raise bad_request(
            f"Invalid {kind} file type",
            f"Allowed: {sorted(list(allowed_ext))}, got: {ext or '(no extension)'}",
        )

    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_BYTES:
        raise too_large(
            f"{kind} too large",
            f"Max bytes: {settings.MAX_UPLOAD_BYTES}, got: {len(data)}",
        )

    return data

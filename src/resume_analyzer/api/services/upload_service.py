from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile

from resume_analyzer.api.config import settings


def save_upload_to_temp(upload: UploadFile, allowed_exts: set[str]) -> Path:
    filename = upload.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    max_bytes = int(settings.MAX_UPLOAD_BYTES)
    size = 0

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f:
        while True:
            chunk = upload.file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                raise HTTPException(status_code=413, detail=f"File too large (max {max_bytes} bytes)")
            f.write(chunk)

        return Path(f.name)

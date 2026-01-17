from __future__ import annotations

from pathlib import Path

from .clean import clean_text
from .docx import extract_text_from_docx
from .pdf import extract_text_from_pdf


SUPPORTED_EXTS = {".pdf", ".docx"}


def extract_resume_text(file_path: str | Path) -> str:
    """
    Extract and clean resume text from supported formats.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"Unsupported resume type: {ext}. Use PDF or DOCX.")

    if ext == ".pdf":
        raw = extract_text_from_pdf(path)
    else:
        raw = extract_text_from_docx(path)

    return clean_text(raw)

from __future__ import annotations

from pathlib import Path
from docx import Document


def extract_text_from_docx(file_path: str | Path) -> str:
    """
    Extract text from a DOCX file.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX not found: {path}")

    doc = Document(str(path))
    parts: list[str] = []

    for p in doc.paragraphs:
        text = (p.text or "").strip()
        if text:
            parts.append(text)

    return "\n".join(parts).strip()

from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str | Path) -> str:
    """
    Extract text from a text-based PDF using pypdf.
    Note: Scanned image PDFs will produce little/empty text (OCR is separate).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(str(path))
    chunks: list[str] = []

    for page in reader.pages:
        txt = page.extract_text() or ""
        if txt.strip():
            chunks.append(txt)

    return "\n".join(chunks).strip()

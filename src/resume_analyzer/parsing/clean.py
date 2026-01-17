import re


def clean_text(text: str) -> str:
    """
    Light cleanup that keeps meaning but removes junk spacing.
    """
    if not text:
        return ""

    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove repeated spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Trim lines
    lines = [ln.strip() for ln in text.split("\n")]
    return "\n".join(lines).strip()

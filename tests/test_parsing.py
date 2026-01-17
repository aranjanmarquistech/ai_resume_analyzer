from pathlib import Path

import pytest

from resume_analyzer.parsing.clean import clean_text
from resume_analyzer.parsing.resume import extract_resume_text


def test_clean_text_basic():
    raw = "Hello   world\r\n\r\n\r\nThis\t\tis   a test"
    cleaned = clean_text(raw)
    assert "Hello world" in cleaned
    assert "\n\n" in cleaned
    assert "\t" not in cleaned


def test_extract_resume_text_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_resume_text("no_such_file.pdf")


def test_extract_resume_text_unsupported_extension(tmp_path: Path):
    f = tmp_path / "resume.txt"
    f.write_text("hi", encoding="utf-8")
    with pytest.raises(ValueError):
        extract_resume_text(f)

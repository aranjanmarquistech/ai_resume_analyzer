from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional


_EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b")
# Loose but practical: handles +91, spaces, dashes, parentheses
# Loose but practical: supports +91 98765 43210, (022) 2345-6789, +1 (415) 555-2671, etc.
_PHONE_RE = re.compile(r"(?<!\w)(?:\+?\(?\d[\d\s\-()]{8,}\d)(?!\w)")

_URL_RE = re.compile(
    r"\bhttps?://[^\s)]+|\bwww\.[^\s)]+", re.IGNORECASE
)

_LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/[^\s)]+", re.IGNORECASE)
_GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/[^\s)]+", re.IGNORECASE)


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        k = x.strip()
        if not k:
            continue
        if k.lower() in seen:
            continue
        seen.add(k.lower())
        out.append(k)
    return out


def normalize_url(url: str) -> str:
    url = url.strip().rstrip(".,;")
    if url.lower().startswith("www."):
        url = "https://" + url
    return url


def normalize_phone(phone: str) -> str:
    phone = phone.strip()
    plus = "+" if phone.startswith("+") else ""
    digits = re.sub(r"\D", "", phone)

    # Most phone numbers are 10–15 digits including country code
    if len(digits) < 10 or len(digits) > 15:
        return ""

    return plus + digits



@dataclass(frozen=True)
class ContactInfo:
    email: Optional[str]
    phones: List[str]
    links: List[str]
    linkedin: Optional[str]
    github: Optional[str]


def extract_contact_info(text: str) -> ContactInfo:
    if not text:
        return ContactInfo(email=None, phones=[], links=[], linkedin=None, github=None)

    emails = _dedupe_keep_order(_EMAIL_RE.findall(text))
    urls = _dedupe_keep_order([normalize_url(u) for u in _URL_RE.findall(text)])
    phones_raw = _PHONE_RE.findall(text)

    phones_norm = []
    for p in phones_raw:
        np = normalize_phone(p)
        if np:
            phones_norm.append(np)
    phones = _dedupe_keep_order(phones_norm)

    linkedin_matches = _dedupe_keep_order([normalize_url(m.group(0)) for m in _LINKEDIN_RE.finditer(text)])
    github_matches = _dedupe_keep_order([normalize_url(m.group(0)) for m in _GITHUB_RE.finditer(text)])

    return ContactInfo(
        email=emails[0] if emails else None,
        phones=phones,
        links=urls,
        linkedin=linkedin_matches[0] if linkedin_matches else None,
        github=github_matches[0] if github_matches else None,
    )

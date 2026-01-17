from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class SkillsTaxonomy:
    canonical_to_aliases: Dict[str, List[str]]
    alias_to_canonical: Dict[str, str]


def load_taxonomy(path: str | Path) -> SkillsTaxonomy:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Skills taxonomy not found: {p}")

    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("skills_taxonomy.json must be a JSON object")

    canonical_to_aliases: Dict[str, List[str]] = {}
    alias_to_canonical: Dict[str, str] = {}

    for canonical, aliases in data.items():
        if not isinstance(canonical, str):
            continue
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            raise ValueError(f"Invalid aliases list for '{canonical}'")

        canon_norm = canonical.strip().lower()
        canonical_to_aliases[canon_norm] = [a.strip().lower() for a in aliases if a.strip()]

        # Include canonical itself as an alias too
        if canon_norm not in canonical_to_aliases[canon_norm]:
            canonical_to_aliases[canon_norm].append(canon_norm)

        for a in canonical_to_aliases[canon_norm]:
            # first one wins if duplicates exist
            alias_to_canonical.setdefault(a, canon_norm)

    return SkillsTaxonomy(
        canonical_to_aliases=canonical_to_aliases,
        alias_to_canonical=alias_to_canonical,
    )

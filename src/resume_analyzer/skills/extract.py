from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from .taxonomy import SkillsTaxonomy, load_taxonomy


_WORD_BOUNDARY = r"(?<![A-Za-z0-9]){alias}(?![A-Za-z0-9])"


def _compile_patterns(tax: SkillsTaxonomy) -> list[tuple[re.Pattern, str]]:
    patterns: list[tuple[re.Pattern, str]] = []

    for alias, canonical in tax.alias_to_canonical.items():
        # Escape alias for regex, keep dots etc literal
        esc = re.escape(alias)
        pattern = re.compile(_WORD_BOUNDARY.format(alias=esc), re.IGNORECASE)
        patterns.append((pattern, canonical))

    # Prefer longer aliases first (e.g., "spring boot" before "boot")
    patterns.sort(key=lambda x: len(x[0].pattern), reverse=True)
    return patterns


class SkillsExtractor:
    def __init__(self, taxonomy_path: str | Path):
        self.taxonomy = load_taxonomy(taxonomy_path)
        self.patterns = _compile_patterns(self.taxonomy)

    def extract(self, text: str) -> Set[str]:
        if not text:
            return set()

        found: Set[str] = set()
        for pat, canonical in self.patterns:
            if pat.search(text):
                found.add(canonical)
        return found


# Convenience function (simple usage)
_default_extractor: Optional[SkillsExtractor] = None


def extract_skills(text: str, taxonomy_path: str | Path = "data/skills_taxonomy.json") -> Set[str]:
    global _default_extractor
    if _default_extractor is None:
        _default_extractor = SkillsExtractor(taxonomy_path)
    return _default_extractor.extract(text)

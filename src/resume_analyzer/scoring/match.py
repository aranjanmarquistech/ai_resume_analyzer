from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_analyzer.skills.extract import extract_skills


@dataclass(frozen=True)
class MatchResult:
    similarity_score: float         # 0..1
    skill_coverage: float           # 0..1
    final_score: float              # 0..1
    resume_skills: List[str]
    jd_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]



def _safe_round(x: float) -> float:
    if x < 0:
        return 0.0
    if x > 1:
        return 1.0
    return float(x)


def compute_text_similarity(resume_text: str, jd_text: str) -> float:
    """
    TF-IDF cosine similarity baseline.
    """
    resume_text = resume_text or ""
    jd_text = jd_text or ""

    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    vect = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    X = vect.fit_transform([resume_text, jd_text])
    sim = cosine_similarity(X[0], X[1])[0][0]
    return _safe_round(sim)


def compute_skill_gap(resume_text: str, jd_text: str) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Returns (resume_skills, jd_skills, missing_skills)
    missing = jd - resume
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    missing = jd_skills - resume_skills
    return resume_skills, jd_skills, missing


def match_resume_to_jd(
    resume_text: str,
    jd_text: str,
    weight_similarity: float = 0.6,
    weight_skill: float = 0.4,
) -> MatchResult:
    """
    Combine TF-IDF similarity + skill coverage.
    """
    sim = compute_text_similarity(resume_text, jd_text)

    resume_skills, jd_skills, missing = compute_skill_gap(resume_text, jd_text)
    matched = jd_skills & resume_skills

    if jd_skills:
        coverage = len(matched) / len(jd_skills)
    else:
        coverage = 0.0

    coverage = _safe_round(coverage)

    # Normalize weights just in case
    total_w = weight_similarity + weight_skill
    if total_w <= 0:
        weight_similarity, weight_skill = 0.6, 0.4
        total_w = 1.0

    w_sim = weight_similarity / total_w
    w_skill = weight_skill / total_w

    final = _safe_round((w_sim * sim) + (w_skill * coverage))

    return     MatchResult(
        similarity_score=sim,
        skill_coverage=coverage,
        final_score=final,
        resume_skills=sorted(resume_skills),
        jd_skills=sorted(jd_skills),
        matched_skills=sorted(matched),
        missing_skills=sorted(missing),
    )


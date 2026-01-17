from __future__ import annotations

from typing import Optional

from resume_analyzer.ml.role_predictor import RolePredictor
from resume_analyzer.parsing.contact import extract_contact_info
from resume_analyzer.parsing.resume import extract_resume_text
from resume_analyzer.scoring.match import match_resume_to_jd
from resume_analyzer.skills.extract import extract_skills


def analyze_resume(resume_path: str, jd_text: Optional[str] = None) -> dict:
    resume_text = extract_resume_text(resume_path)

    contact = extract_contact_info(resume_text)
    skills = sorted(extract_skills(resume_text))

    result: dict = {
        "contact": {
            "email": contact.email,
            "phones": contact.phones,
            "linkedin": contact.linkedin,
            "github": contact.github,
            "links": contact.links,
        },
        "skills": skills,
        "role_prediction": [],
        "role_model": None,
        "match": None,
    }

    # role prediction (top 3)
    try:
        predictor = RolePredictor()  # loads latest from latest_role_model.txt
        top3 = predictor.predict_topk(resume_text, k=3)
        result["role_prediction"] = [{"label": r.label, "confidence": r.confidence} for r in top3]
        result["role_model"] = str(predictor.model_path)
    except Exception:
        pass

    # JD match (only if jd_text present)
    if jd_text and jd_text.strip():
        m = match_resume_to_jd(resume_text, jd_text)
        result["match"] = {
            "similarity_score": m.similarity_score,
            "skill_coverage": m.skill_coverage,
            "final_score": m.final_score,
            "resume_skills": m.resume_skills,
            "jd_skills": m.jd_skills,
            "matched_skills": m.matched_skills,
            "missing_skills": m.missing_skills,
        }

    return result

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote

from resume_analyzer.ml.role_predictor import RolePredictor
from resume_analyzer.parsing.contact import extract_contact_info
from resume_analyzer.parsing.resume import extract_resume_text
from resume_analyzer.scoring.match import match_resume_to_jd
from resume_analyzer.skills.extract import extract_skills
from resume_analyzer.utils.logging import setup_logging


def normalize_path(p: str) -> str:
    """
    Accepts normal Windows paths and file:/// URLs.
    Converts file:///C:/Users/... -> C:/Users/...
    """
    p = (p or "").strip()
    if p.lower().startswith("file:"):
        u = urlparse(p)
        p = unquote(u.path.lstrip("/"))
    return p


def read_text_file(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JD file not found: {p}")
    return p.read_text(encoding="utf-8", errors="ignore")


def main() -> None:
    setup_logging()
    log = logging.getLogger("resume_analyzer.cli")

    parser = argparse.ArgumentParser(
        prog="resume-analyzer",
        description="Analyze a resume and optionally match it against a Job Description (JD).",
    )

    parser.add_argument("--resume", required=True, help="Path to resume file (.pdf or .docx)")
    parser.add_argument("--jd-file", help="Path to JD text file (.txt)")
    parser.add_argument("--jd-text", help="JD as raw text (alternative to --jd-file)")
    parser.add_argument("--out", help="Optional output file path (json/text based on --format)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--top-missing", type=int, default=0, help="Show only top N missing skills (0 = all)")

    args = parser.parse_args()

    resume_path = normalize_path(args.resume)
    resume_file_abs = str(Path(resume_path).resolve())

    # Parse resume text
    resume_text = extract_resume_text(resume_path)
    log.info("Parsed resume file successfully: %s", resume_file_abs)

    # Role prediction (optional)
    role_pred = None
    try:
        predictor = RolePredictor()
        role_pred = predictor.predict_topk(resume_text, k=3)

    except Exception as e:
        # Don't crash CLI if model isn't present; just log for debugging.
        log.debug("Role prediction skipped: %s", e)

    # Contact + skills
    contact = extract_contact_info(resume_text)
    resume_skills = sorted(extract_skills(resume_text))

    result: dict = {
        "resume_file": resume_file_abs,
        "contact": {
            "email": contact.email,
            "phones": contact.phones,
            "linkedin": contact.linkedin,
            "github": contact.github,
            "links": contact.links,
        },
        "skills": resume_skills,
    }

    if role_pred:
        result["role_prediction"] = [
            {"label": r.label, "confidence": r.confidence} for r in role_pred
        ]

    # JD input
    jd_text = None
    if args.jd_text and args.jd_text.strip():
        jd_text = args.jd_text
    elif args.jd_file:
        jd_text = read_text_file(normalize_path(args.jd_file))

    # Match (if JD provided)
    if jd_text:
        match = match_resume_to_jd(resume_text, jd_text)

        missing = match.missing_skills
        if args.top_missing and args.top_missing > 0:
            missing = missing[: args.top_missing]

        result["match"] = {
            "similarity_score": match.similarity_score,
            "skill_coverage": match.skill_coverage,
            "final_score": match.final_score,
            "resume_skills": match.resume_skills,
            "jd_skills": match.jd_skills,
            "matched_skills": match.matched_skills,
            "missing_skills": missing,
        }

    # Output formatting
    if args.format == "text":
        lines: list[str] = []
        lines.append(f"Resume: {result['resume_file']}")
        lines.append(f"Email: {result['contact']['email']}")
        lines.append(f"Phones: {', '.join(result['contact']['phones']) if result['contact']['phones'] else '-'}")

        if "role_prediction" in result:
            top = result["role_prediction"]
            pretty = ", ".join([f"{r['label']} ({r['confidence']:.2f})" for r in top])
            lines.append(f"Predicted Roles: {pretty}")

        lines.append(f"Skills ({len(result['skills'])}): {', '.join(result['skills']) if result['skills'] else '-'}")

        if "match" in result:
            m = result["match"]
            lines.append("")
            lines.append(
                f"Match Score: {m['final_score']:.2f} "
                f"(Similarity {m['similarity_score']:.2f}, Coverage {m['skill_coverage']:.2f})"
            )
            lines.append(f"JD Skills ({len(m['jd_skills'])}): {', '.join(m['jd_skills']) if m['jd_skills'] else '-'}")
            lines.append(f"Matched ({len(m['matched_skills'])}): {', '.join(m['matched_skills']) if m['matched_skills'] else '-'}")
            lines.append(f"Missing ({len(m['missing_skills'])}): {', '.join(m['missing_skills']) if m['missing_skills'] else '-'}")

        output = "\n".join(lines)
    else:
        output = json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False)

    # Write or print
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"✅ Saved: {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()

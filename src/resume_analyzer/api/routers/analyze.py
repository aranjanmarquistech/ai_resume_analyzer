from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile

from resume_analyzer.api.schemas import AnalyzeResponse, ContactOut, MatchOut, RolePredictionOut
from resume_analyzer.api.security import require_api_key
from resume_analyzer.api.services.analyze_service import analyze_resume
from resume_analyzer.api.services.upload_service import save_upload_to_temp

router = APIRouter(tags=["analyze"])

ALLOWED_RESUME_EXTS = {".pdf", ".docx"}
ALLOWED_JD_EXTS = {".txt", ".pdf", ".docx"}


@router.post("/analyze", response_model=AnalyzeResponse, dependencies=[Depends(require_api_key)])
async def analyze(
    resume: UploadFile = File(...),
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
):
    tmp_resume = save_upload_to_temp(resume, ALLOWED_RESUME_EXTS)

    tmp_jd_path = None
    try:
        jd_final = None

        if jd_text and jd_text.strip():
            jd_final = jd_text.strip()
        elif jd_file is not None:
            tmp_jd_path = save_upload_to_temp(jd_file, ALLOWED_JD_EXTS)
            ext = Path(jd_file.filename or "").suffix.lower()
            if ext == ".txt":
                jd_final = tmp_jd_path.read_text(encoding="utf-8", errors="ignore")
            else:
                from resume_analyzer.parsing.resume import extract_resume_text
                jd_final = extract_resume_text(str(tmp_jd_path))

        data = analyze_resume(str(tmp_resume), jd_final)

        return AnalyzeResponse(
            resume_filename=resume.filename,
            contact=ContactOut(**data["contact"]),
            skills=data["skills"],
            role_prediction=[RolePredictionOut(**x) for x in data["role_prediction"]],
            role_model=data["role_model"],
            match=MatchOut(**data["match"]) if data["match"] else None,
        )
    finally:
        tmp_resume.unlink(missing_ok=True)
        if tmp_jd_path is not None:
            tmp_jd_path.unlink(missing_ok=True)

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response


from .auth import require_api_key
from .config import settings
from .deps import ALLOWED_JD_EXT, ALLOWED_RESUME_EXT, validate_upload
from .schemas import AnalyzeResponse, ContactOut, MatchOut, RolePredictionOut

# ✅ Your existing “already working” pipeline functions
from resume_analyzer.parsing.resume import extract_resume_text
from resume_analyzer.parsing.contact import extract_contact_info
from resume_analyzer.skills.extract import extract_skills
from resume_analyzer.scoring.match import match_resume_to_jd
from resume_analyzer.ml.role_predictor import RolePredictor


def _bytes_to_tempfile(data: bytes, filename: str) -> Path:
    """
    Writes bytes to a temp file with the same extension as filename
    so your existing extract_resume_text(path) can be reused.
    """
    suffix = Path(filename).suffix or ".bin"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(data)
        tmp.flush()
        return Path(tmp.name)
    finally:
        (tmp.close()

         @app.get("/favicon.ico", include_in_schema=False))
        def favicon():
            return Response(status_code=204)


def create_app() -> FastAPI:
    app = FastAPI(title="Resume Analyzer", version=settings.API_VERSION)

    # CORS
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    allow_all = "*" in origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else origins,
        allow_credentials=False if allow_all else True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {
            "name": "Resume Analyzer API",
            "status": "running",
            "docs": "/docs",
            "health": "/health",
            "analyze": "/analyze",
        }

    @app.get("/health")
    def health():
        return {"status": "ok", "version": settings.API_VERSION}

    @app.post(
        "/analyze",
        response_model=AnalyzeResponse,
        responses={
            400: {"model": dict},
            401: {"model": dict},
            413: {"model": dict},
        },
    )
    async def analyze(
        resume: UploadFile = File(...),
        jd_file: UploadFile | None = File(None),
        jd_text: str | None = Form(None),
        _: str = Depends(require_api_key),
    ) -> AnalyzeResponse:
        # 1) Validate + read files
        resume_bytes = await validate_upload(resume, ALLOWED_RESUME_EXT, "resume")

        jd_bytes: bytes | None = None
        if jd_file is not None:
            jd_bytes = await validate_upload(jd_file, ALLOWED_JD_EXT, "jd_file")

        # 2) Resume bytes -> text (reuse your existing extractor)
        resume_tmp = _bytes_to_tempfile(resume_bytes, resume.filename or "resume.pdf")
        try:
            resume_text = extract_resume_text(str(resume_tmp))
        finally:
            resume_tmp.unlink(missing_ok=True)

        # 3) Contact + skills
        contact = extract_contact_info(resume_text)
        skills = sorted(extract_skills(resume_text))

        # 4) Role prediction (optional)
        role_prediction: list[RolePredictionOut] = []
        role_model: str | None = None
        try:
            predictor = RolePredictor("models/role_pipeline.joblib")
            pred = predictor.predict(resume_text)  # your current class supports this
            role_prediction = [
                RolePredictionOut(label=pred.label, confidence=float(pred.confidence))
            ]
            role_model = "models/role_pipeline.joblib"
        except Exception:
            role_prediction = []
            role_model = None

        # 5) JD final text (from jd_text or jd_file)
        jd_final_text: str | None = None

        if jd_text and jd_text.strip():
            jd_final_text = jd_text.strip()
        elif jd_bytes is not None and jd_file is not None:
            # If JD is txt, decode. If pdf/docx, parse like resume.
            ext = (Path(jd_file.filename).suffix or "").lower()
            if ext == ".txt":
                jd_final_text = jd_bytes.decode("utf-8", errors="ignore")
            else:
                jd_tmp = _bytes_to_tempfile(jd_bytes, jd_file.filename)
                try:
                    jd_final_text = extract_resume_text(str(jd_tmp))
                finally:
                    jd_tmp.unlink(missing_ok=True)

        # 6) Match (only if JD exists)
        match_out: MatchOut | None = None
        if jd_final_text and jd_final_text.strip():
            m = match_resume_to_jd(resume_text, jd_final_text)
            match_out = MatchOut(
                similarity_score=float(m.similarity_score),
                skill_coverage=float(m.skill_coverage),
                final_score=float(m.final_score),
                resume_skills=list(m.resume_skills),
                jd_skills=list(m.jd_skills),
                matched_skills=list(m.matched_skills),
                missing_skills=list(m.missing_skills),
            )

        # 7) Return typed DTO response
        return AnalyzeResponse(
            resume_filename=resume.filename,
            contact=ContactOut(
                email=contact.email,
                phones=contact.phones,
                linkedin=contact.linkedin,
                github=contact.github,
                links=contact.links,
            ),
            skills=skills,
            role_prediction=role_prediction,
            role_model=role_model,
            match=match_out,
        )

    return app


app = create_app()

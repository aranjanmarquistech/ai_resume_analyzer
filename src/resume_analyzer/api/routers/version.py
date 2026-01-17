from fastapi import APIRouter

from resume_analyzer.api.config import settings

router = APIRouter(tags=["version"])


@router.get("/version")
def version():
    return {"api_version": settings.API_VERSION}

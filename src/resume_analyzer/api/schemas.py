from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class ContactOut(BaseModel):
    email: Optional[str] = None
    phones: List[str] = Field(default_factory=list)
    linkedin: Optional[str] = None
    github: Optional[str] = None
    links: List[str] = Field(default_factory=list)


class RolePredictionOut(BaseModel):
    label: str
    confidence: float


class MatchOut(BaseModel):
    similarity_score: float
    skill_coverage: float
    final_score: float
    resume_skills: List[str] = Field(default_factory=list)
    jd_skills: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    resume_filename: Optional[str] = None
    contact: ContactOut
    skills: List[str] = Field(default_factory=list)
    role_prediction: List[RolePredictionOut] = Field(default_factory=list)
    role_model: Optional[str] = None
    match: Optional[MatchOut] = None

from typing import List, Literal, Optional

from pydantic import BaseModel

from app.api.models.candidate_profile import CandidateProfile


class Response(BaseModel):
    id: Optional[str] = None
    relevance_score: Optional[float] = None
    name: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    current_city: Optional[str] = None
    job_role: Optional[str] = None
    job_title: Optional[str] = None
    total_months_of_experience: Optional[int] = None
    skills: Optional[list[str]] = None
    job_role_score: Optional[float] = None
    job_title_score: Optional[float] = None
    skills_score: Optional[float] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None

class JobResponse(BaseModel):
    id: Optional[str] = None
    relevance_score: Optional[int] = None
    company: Optional[str] = None
    location: Optional[list[str]] = None
    experience_required: Optional[float] = None
    salary: Optional[float] = None
    description: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None
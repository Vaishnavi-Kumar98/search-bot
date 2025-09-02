from typing import List, Optional
from pydantic import BaseModel

class Organisations(BaseModel):
    organisation_name: Optional[str]
    job_title: Optional[str]
    role: Optional[str]
    industry: Optional[str]
    employment_type: Optional[str]
    is_current_job: Optional[int]

class Education(BaseModel):
    education_level: Optional[str]
    course_name: Optional[str]
    specialization: Optional[str]
    year_of_completion: Optional[int]
    course_type: Optional[str]
    is_highest_qualification: Optional[int]

class Salary(BaseModel):
    expected_annual_ctc: Optional[float]
    current_annual_ctc: Optional[float]

class CandidateProfile(BaseModel):
    id: str
    first_name: Optional[str]
    last_name: Optional[str]
    primary_mobile_number: Optional[str]
    primary_email: Optional[str]
    current_city: Optional[str]
    preferred_cities: Optional[List[str]]
    total_months_of_experience: Optional[int]
    skills: Optional[List[str]]
    employment_history: Optional[List[Organisations]]
    education_details: Optional[List[Education]]
    expected_annual_ctc: Optional[float]
    current_annual_ctc: Optional[float]
    created_at: Optional[int] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
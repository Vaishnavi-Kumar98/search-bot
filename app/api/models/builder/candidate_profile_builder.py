import uuid
from typing import Dict, Any, List, Optional


class CandidateProfileBuilder:
    """
    Builder class that transforms parsed LLM resume output
    into Vespa-compatible candidate schema.
    """

    def __init__(self, llm_data: Dict[str, Any]):
        self.data = llm_data

    def build_user_profile(self) -> Dict[str, Any]:
        return {
            "id": self._generate_id(),
            "first_name": self._get_first_name(),
            "last_name": self._get_last_name(),
            "primary_mobile_number": self._get_primary_mobile_number(),
            "primary_email": self._get_primary_email(),
            "current_city": self._get_current_city(),
            "preferred_cities": self._get_preferred_cities(),
            "total_months_of_experience": self._get_total_experience_months(),
            "skills": self.data.get("skills", []),
            "employment_history": self._map_employment_history(),
            "education_details": self._map_education(),
            "expected_annual_ctc": self.data.get("expectedctc"),
            "current_annual_ctc": self.data.get("currentctc"),
        }

    def _generate_id(self) -> str:
        return f"cand-{uuid.uuid4().hex[:8]}"

    def _get_first_name(self) -> Optional[str]:
        name = self.data.get("name")
        return name.split()[0] if name else None

    def _get_last_name(self) -> Optional[str]:
        name = self.data.get("name")
        return name.split(" ", 1)[1] if name and " " in name else None

    def _get_primary_mobile_number(self) -> Optional[str]:
        mobile = self.data.get("mobile")
        if isinstance(mobile, list) and mobile:
            return mobile[0]
        if isinstance(mobile, str):
            return mobile
        return None

    def _get_primary_email(self) -> Optional[str]:
        email = self.data.get("email")
        if isinstance(email, list) and email:
            return email[0]
        if isinstance(email, str):
            return email
        return None

    def _get_current_city(self) -> Optional[str]:
        address = self.data.get("address", {})
        return address.get("location")

    def _get_preferred_cities(self) -> List[str]:
        preferred = self.data.get("preferred_cities", [])
        return preferred

    def _get_total_experience_months(self) -> int:
        years = self.data.get("workexperience", {}).get("totalyearsofexperience")
        return int(years * 12) if years else 0

    def _map_employment_history(self) -> List[Dict[str, Any]]:
        work_history = self.data.get("workexperience", {}).get("workhistory", [])
        mapped = []
        for job in work_history:
            mapped.append({
                "organisation_name": job.get("organisation"),
                "job_title": job.get("jobtitle"),
                "role": job.get("role"),
                "industry": job.get("industry"),
                "employment_type": job.get("employmenttype"),
                "is_current_job": 1 if job.get("islatest") else 0
            })
        return mapped

    def _map_education(self) -> List[Dict[str, Any]]:
        education = self.data.get("education", [])
        mapped = []
        for edu in education:
            mapped.append({
                "education_level": edu.get("course"),
                "course_name": edu.get("course"),
                "specialization": edu.get("specialization"),
                "year_of_completion": self._safe_int(edu.get("yearofpassing")),
                "course_type": edu.get("coursetype"),
                "is_highest_qualification": 1 if edu.get("islatesteducation") else 0
            })
        return mapped

    def _safe_int(self, val: Any) -> Optional[int]:
        try:
            return int(val) if val is not None else None
        except ValueError:
            return None

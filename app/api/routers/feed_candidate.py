from datetime import datetime
from fastapi import APIRouter, HTTPException
import logging

from app.api.models.candidate_profile import CandidateProfile
from app.api.services.feed_candidate_service import feed_candidate_to_vespa
from app.api.utils.derive_fields import derive_highest_education, derive_latest_job_fields

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/feed")
async def feed_candidate_profiles(profile: CandidateProfile):
    """
    Endpoint to feed a candidate profile into Vespa.
    """
    try:
        latest_job_title, latest_role = derive_latest_job_fields(profile.employment_history)
        highest_education_level, highest_course_year_of_completion = derive_highest_education(profile.education_details)

        # Prepare payload
        vespa_payload = profile.model_dump(exclude_none=True)
        if latest_job_title:
            vespa_payload["latest_job_title"] = latest_job_title
        if latest_role:
            vespa_payload["latest_role"] = latest_role
        if highest_education_level:
            vespa_payload["highest_education_level"] = highest_education_level
        if highest_course_year_of_completion:
            vespa_payload["highest_course_year_of_completion"] = highest_course_year_of_completion

        preferred_cities = vespa_payload.get("preferred_cities", [])
        current_city = vespa_payload.get("current_city")
        if not isinstance(preferred_cities, list):
            preferred_cities = [preferred_cities] if preferred_cities else []
        combined_cities = []
        if current_city:
            combined_cities.append(current_city)
        combined_cities.extend(preferred_cities)
        vespa_payload["preferred_and_current_cities"] = combined_cities

        now_epoch = int(datetime.now().timestamp())
        vespa_payload["created_at"] = now_epoch
        vespa_payload["created_by"] = "TEST_USER"
        vespa_payload["updated_by"] = "TEST_USER"

        # Feed into Vespa
        vespa_response = feed_candidate_to_vespa(
            schema="candidate_profile",
            data_id=profile.id,
            fields=vespa_payload
        )

        return {"message": "Document fed successfully", "vespa_response": vespa_response, "vespa_payload": vespa_payload}
    except Exception as ex:
        logger.error(f"Exception in {__file__} while feeding candidate: {ex}")
        raise HTTPException(
            status_code=500,
            detail=f"Exception while feeding candidate: {ex}"
        )

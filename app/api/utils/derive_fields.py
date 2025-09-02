import logging
from typing import List, Optional
from app.api.models.candidate_profile import Education, Organisations

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

def derive_latest_job_fields(employment_history: Optional[List[Organisations]]):
    """Extract latest job title & role from current job."""
    try:
        latest_job_title, latest_role = None, None
        if employment_history:
            for job in employment_history:
                if job.is_current_job == 1:
                    latest_job_title = job.job_title
                    latest_role = job.role
                    break
        return latest_job_title, latest_role
    except Exception as ex:
        logger.error(f"Exception in {__file__} while deriving latest job fields: {ex}")
        raise RuntimeError("Error deriving latest job fields") from ex

def derive_highest_education(education_details: Optional[List[Education]]):
    """Extract highest education level & year of completion from qualification flag."""
    try:
        highest_education_level = None
        highest_course_year_of_completion = None
        if education_details:
            for edu in education_details:
                if edu.is_highest_qualification == 1:
                    highest_education_level = edu.education_level
                    highest_course_year_of_completion = edu.year_of_completion
                    break
        return highest_education_level, highest_course_year_of_completion
    except Exception as ex:
        logger.error(f"Exception in {__file__} while deriving highest education: {ex}")
        raise RuntimeError("Error deriving highest education") from ex
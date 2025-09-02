import logging
from typing import Any, Dict

from app.api.models.response import JobResponse

logger = logging.getLogger(__name__)


class JobResponseBuilder:
    def from_query_results(self, query_result: Dict[str, Any]) -> JobResponse:
        try:
            fields = query_result.get("fields", query_result)
            return JobResponse(
                id=fields.get("id"),
                relevance_score=int(query_result.get("relevance") * 100) if query_result.get("relevance") else None,
                company=fields.get("company_name"),
                location=fields.get("location"),
                experience_required=int(fields.get("total_months_of_experience")//12) if fields.get("total_months_of_experience") is not None else None,
                salary=fields.get("annual_ctc"),
                description=fields.get("job_summary"),
                role=fields.get("job_role"),
                title=fields.get("job_title"),
            )
        except Exception as ex:
            logger.error(f"Error building Response object from vespa_response: {ex} | Data: {query_result}")
            raise RuntimeError(f"Error building Response object: {ex}") from ex
from datetime import datetime
import logging
from typing import Any, Dict, Optional

from app.api.models.response import Response

logger = logging.getLogger(__name__)

class ResponseBuilder:
    """
    Builder class to construct Response objects from Vespa result dicts.
    """

    @staticmethod
    def _format_name(first_name: Optional[str], last_name: Optional[str]) -> Optional[str]:
        if first_name and last_name:
            return f"{first_name} {last_name}"
        return first_name or last_name

    @staticmethod
    def _format_created_at(created_at: Optional[float]) -> Optional[str]:
        if created_at is None:
            return None
        try:
            # Handle both ms and s epoch
            divisor = 1000 if created_at > 1e12 else 1
            dt = datetime.fromtimestamp(created_at / divisor)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as ex:
            logger.warning(f"Invalid created_at value: {created_at} ({ex})")
            return None

    def from_query_results(self, query_result: Dict[str, Any]) -> Response:
        """
        Build a Response object from a single Vespa response dict.
        """
        try:
            fields = query_result.get("fields", query_result)
            name = self._format_name(fields.get("first_name"), fields.get("last_name"))
            created_at = self._format_created_at(fields.get("created_at"))
            return Response(
                id=fields.get("id"),
                relevance_score=query_result.get("relevance") * 100 if query_result.get("relevance") else None,
                name=name,
                email=fields.get("primary_email"),
                mobile_number=fields.get("primary_mobile_number"),
                current_city=fields.get("current_city"),
                job_role=fields.get("latest_role"),
                job_title=fields.get("latest_job_title"),
                total_months_of_experience=fields.get("total_months_of_experience"),
                skills=fields.get("skills"),
                job_role_score=fields.get("summaryfeatures", {}).get("latest_role_score") * 100 if fields.get("summaryfeatures", {}).get("latest_role_score") is not None else None,
                job_title_score=fields.get("summaryfeatures", {}).get("latest_title_score") * 100 if fields.get("summaryfeatures", {}).get("latest_title_score") is not None else None,
                skills_score=fields.get("summaryfeatures", {}).get("skills_score") * 100 if fields.get("summaryfeatures", {}).get("skills_score") is not None else None,
                created_at=created_at,
                created_by=fields.get("created_by"),
            )
        except Exception as ex:
            logger.error(f"Error building Response object from vespa_response: {ex} | Data: {query_result}")
            raise RuntimeError(f"Error building Response object: {ex}") from ex
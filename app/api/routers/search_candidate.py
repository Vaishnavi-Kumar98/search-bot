import logging
from typing import Optional
from fastapi import APIRouter, HTTPException

from app.api.models.search_request import SearchRequest
from app.api.services.search_candidate_service import build_query, fetch_results, format_response, validate_pagination
from app.api.utils.query_builder import get_field_presence
from app.api.utils.search_fields_map import candidate_field_map

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/search")
async def search_candidate_profiles(
    request_body: SearchRequest,
    page_number: Optional[str] = "1",
    page_size: Optional[str] = "10",
):
    try:
        limit, offset = validate_pagination(page_number=page_number, page_size=page_size)
        query, nearest_neighbour_inputs = build_query(request_body, candidate_field_map, "candidate_profile", limit, offset)
        field_presence = get_field_presence(request_body.searchParams)
        query_results = fetch_results(query, nearest_neighbour_inputs, field_presence)
        formatted_results = format_response(query_results)
        return formatted_results
    except HTTPException as ex:
        logger.error(f"HTTPException in {__file__}: {ex}")
        raise
    except Exception as ex:
        logger.error(f"Unexpected exception in {__file__}: {ex}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")
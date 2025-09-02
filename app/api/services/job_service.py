import json
from app.api.models.builder.job_response_builder import JobResponseBuilder
from app.api.models.search_request import SearchParams, SearchRequest
from app.api.services.search_candidate_service import build_query, fetch_results, filter_field_data, format_response, validate_pagination
from app.api.utils.query_builder import build_query_for_years_of_experience, build_query_from_list, build_range_query, get_field_presence
from app.api.utils.search_fields_map import job_field_map


def search_job(job_request: SearchRequest):
    """Call the search API with the given search params."""
    print("IM IN SEARCH JOB TOOL ",job_request)
    job_request = SearchRequest(searchType="both",searchParams=job_request.searchParams)
    limit, offset = validate_pagination(page_number="1", page_size="10")
    query, nearest_neighbour_inputs = build_query(job_request, job_field_map, "job", limit, offset)
    field_presence = get_field_presence(job_request.searchParams)
    query_results = fetch_results(query, nearest_neighbour_inputs, field_presence)
    formatted_results = format_jobs(query_results)
    return formatted_results

def format_jobs(query_results: list[dict]):
    try:
        formatted_responses = []
        if query_results:
            for response in query_results:
                result = JobResponseBuilder().from_query_results(response)
                formatted_responses.append(json.loads(result.model_dump_json()))
            return formatted_responses
        else:
            return query_results
    except Exception as ex:
        print("Exception in formatting job response: ",ex)
        # logger.error(f"Exception in {__file__} while formatting response: {ex}")
        raise RuntimeError(
            f"Error while formatting job response: {ex}"
        ) from ex
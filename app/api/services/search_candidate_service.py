import json
import os
import logging
from vespa.application import Vespa
from vespa.io import VespaQueryResponse
from app.api.exceptions.page_invalid_exception import PageInvalidError
from app.api.models.builder.response_builder import ResponseBuilder
from app.api.models.search_request import SearchParams, SearchRequest
from app.api.utils.query_builder import (
    build_query_for_hard_filters,
    build_query_for_soft_filters,
    build_query_for_years_of_experience,
    build_query_from_list,
    build_range_query,
    build_range_query_for_struct_type,
    build_search_query,
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

VESPA_QUERY_URL = os.environ.get("VESPA_QUERY_URL", "http://localhost:8080")

def filter_field_data(data: list[str] | None) -> list[str] | None:
    """Filter out None or empty values from a list of strings."""
    if data is not None:
        return list(filter(None, data))
    return None

def validate_pagination(page_number: str, page_size: str) -> tuple[int, int]:
    """Validate and calculate pagination parameters."""
    try:
        page_number = int(page_number)
        page_size = int(page_size)
    except (TypeError, ValueError) as ex:
        logger.error(f"Invalid pagination input in {__file__}: {ex}")
        raise PageInvalidError("Page number and size must be integers") from ex

    if page_number <= 0 or page_size <= 0 or page_size > 400:
        logger.error(f"Invalid page number/size in {__file__}: page_number={page_number}, page_size={page_size}")
        raise PageInvalidError("Page Number/Page Size is invalid")

    limit = page_number * page_size
    offset = (page_number * page_size) - page_size

    if offset > 1000:
        logger.error(f"Offset too large in {__file__}: offset={offset}")
        raise PageInvalidError("Offset too large")

    return limit, offset

def build_query(request_body: SearchRequest, field_map: dict, schema:str, limit: int, offset: int) -> tuple[str, dict]:
    """Build the Vespa query and semantic input dictionary."""
    try:
        hard_filter_query = None
        soft_filter_query = None
        nearest_neighbour_query = None
        nearest_neighbour_inputs = {}
        search_type = request_body.searchType.value
        search_params = request_body.searchParams
        if search_type != 1:
            list_of_filters = create_hard_filter(search_params, field_map, search_type)
            hard_filter_query = build_query_for_hard_filters(list_of_filters)
        if search_type != 0:
            list_of_soft_filters = create_soft_filters(search_params, field_map)
            soft_filter_query = build_query_for_soft_filters(list_of_soft_filters)
            nearest_neighbour_inputs, nearest_neighbour_query = build_semantic_query_for_fields(search_params, field_map)
        query = build_search_query(schema, hard_filter_query, soft_filter_query, nearest_neighbour_query)
        if query is None:
            logger.error(f"Query construction failed")
            raise RuntimeError("Query construction failed")
        query = f"{query} limit {limit} offset {offset}"
        logger.info(f"Query built: {query}")
        return query, nearest_neighbour_inputs
    except Exception as ex:
        logger.error(f"Exception in {__file__} while building query: {ex}")
        raise RuntimeError(
            f"Error while building query: {ex}"
        ) from ex

def create_hard_filter(search_params: SearchParams, candidate_field_map: dict, search_type: int) -> list:
    """Create hard filter query list based on search parameters."""
    try:
        query_list = []
        if search_type == 0:
            exact_skills_filter = build_query_from_list(
                field_name=candidate_field_map.get("skills_exact"), field_data=search_params.skills, filter_type="contains"
            )
            role_filter = build_query_from_list(
                field_name=candidate_field_map.get("jobRole"),
                field_data=search_params.jobRole,
                filter_type="contains",
            )
            title_filter = build_query_from_list(
                field_name=candidate_field_map.get("jobTitle"),
                field_data=search_params.jobTitle,
                filter_type="contains",
            )
            query_list.extend([exact_skills_filter, role_filter, title_filter])
        city_filter = build_query_from_list(
            field_name=candidate_field_map.get("location"),
            field_data=filter_field_data(search_params.location),
            filter_type="contains",
        )
        years_of_experience_filter = build_query_for_years_of_experience(
            field_name=candidate_field_map.get("yearsOfExperience"),
            range_from=search_params.experienceMin,
            range_to=search_params.experienceMax,
        )
        expected_annual_ctc_filter = build_range_query(
            field_name=candidate_field_map.get("ctc"),
            range_from=search_params.expectedSalaryMin,
            range_to=search_params.expectedSalaryMax,
        )
        query_list.extend(
            [
                city_filter,
                years_of_experience_filter,
                expected_annual_ctc_filter
            ]
        )
        return query_list
    except Exception as ex:
        logger.error(f"Exception in {__file__} while creating hard filters: {ex}")
        raise RuntimeError(
            f"Error while creating hard filters: {ex}"
        ) from ex

def create_soft_filters(search_params: SearchParams, candidate_field_map:dict) -> list:
    """Create soft filter query list based on search parameters."""
    try:
        query_list = []
        exact_skills_filter = build_query_from_list(
            field_name=candidate_field_map.get("skills"), field_data=search_params.skills, filter_type="contains"
        )
        role_filter = build_query_from_list(
            field_name=candidate_field_map.get("jobRole"),
            field_data=search_params.jobRole,
            filter_type="contains",
        )
        title_filter = build_query_from_list(
            field_name=candidate_field_map.get("jobTitle"),
            field_data=search_params.jobTitle,
            filter_type="contains",
        )
        query_list.extend([exact_skills_filter, role_filter, title_filter])
        return query_list
    except Exception as ex:
        logger.error(f"Exception in {__file__} while creating soft filters: {ex}")
        raise RuntimeError(
            f"Error while creating soft filters: {ex}"
        ) from ex

def build_semantic_query_for_fields(search_params: SearchParams, candidate_field_map:dict) -> tuple[dict, str | None]:
    """Build semantic query dict and nearest neighbour query string for Vespa."""
    try:
        semantic_query_dict = {}
        nearest_neighbour_query_list = []
        semantic_fields_with_input = {
            "skills": {
                "tensor": "s",
                "embedding": candidate_field_map.get("skillsEmbedding"),
                "model": "e5-small-skills-v1",
            },
            "jobRole": {
                "tensor": "r",
                "embedding": candidate_field_map.get("roleEmbedding"),
                "model": "e5-small-finetuned-role-title",
            },
            "jobTitle": {
                "tensor": "t",
                "embedding": candidate_field_map.get("titleEmbedding"),
                "model": "e5-small-finetuned-role-title",
            },
        }
        for name, value in vars(search_params).items():
            if name in semantic_fields_with_input and value:
                tensor = semantic_fields_with_input[name]['tensor']
                embedding = semantic_fields_with_input[name]['embedding']
                model = semantic_fields_with_input[name]['model']
                if name == "skills":
                    role_with_skills = search_params.jobRole + value if search_params.jobRole else value
                    value = [",".join(role_with_skills)] if role_with_skills else None
                semantic_query_dict[f"input.query({tensor})"] = (
                    f"embed({model},'{' '.join(value)}')"
                )
                nearest_neighbour_query_list.append(
                    f"({{targetHits:10}}nearestNeighbor({embedding},{tensor}))"
                )
        nearest_neighbour_query = (
            " OR ".join(nearest_neighbour_query_list)
            if nearest_neighbour_query_list
            else None
        )
        return semantic_query_dict, nearest_neighbour_query
    except Exception as ex:
        logger.error(f"Exception in {__file__} while building semantic query: {ex}")
        raise RuntimeError(
            f"Error while building semantic query for fields: {ex}"
        ) from ex

def fetch_results(
    query: str,
    nearest_neighbour_inputs: dict | None,
    field_presence: dict | None
) -> VespaQueryResponse:
    """Fetch results from Vespa using the constructed query and inputs."""
    try:
        app = Vespa(url=VESPA_QUERY_URL)
        if nearest_neighbour_inputs is None:
            nearest_neighbour_inputs = {}
        if field_presence:
            nearest_neighbour_inputs.update(field_presence)
        logger.info(f"Nearest neighbour inputs: {nearest_neighbour_inputs}")
        with app.syncio() as session:
            response: VespaQueryResponse = session.query(
                yql=query,
                ranking="default",
                body=nearest_neighbour_inputs,
                timeout=20,
            ).get_json()
            return response.get("root", {}).get("children", None)
    except Exception as ex:
        logger.error(f"Exception in {__file__} while fetching results: {ex}")
        raise RuntimeError(
            f"Error while fetching results: {ex}"
        ) from ex

def format_response(responses: list[dict]):
    try:
        formatted_responses = []
        if responses:
            for response in responses:
                result = ResponseBuilder().from_query_results(response)
                formatted_responses.append(json.loads(result.model_dump_json()))
            return formatted_responses
        else:
            return responses
    except Exception as ex:
        logger.error(f"Exception in {__file__} while formatting response: {ex}")
        raise RuntimeError(
            f"Error while formatting response: {ex}"
        ) from ex


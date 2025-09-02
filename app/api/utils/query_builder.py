

import logging
from app.api.utils.search_fields_map import search_input_fields

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

def build_range_query(
        field_name: str, range_from: float | None, range_to: float | None
    ):
    try:
        if range_to and range_from:
            range_filter = (
                f"(range({field_name}, {range_from}, {range_to}))"
            )
            return range_filter
        elif range_from and (not range_to):
            range_filter = f"({field_name} >= {range_from})"
            return range_filter
        elif range_to and (not range_from):
            range_filter = f"({field_name} <= {range_to})"
            return range_filter
        return None
    except Exception as ex:
        logger.error(f"Error while building RANGE query for '{field_name}' in {__file__}: {ex}")
        raise RuntimeError(
            f"Error while building RANGE query for '{field_name}': {ex}"
        ) from ex
        

def build_query_for_years_of_experience(
        field_name: str, range_from: float | None, range_to: float | None
    ):
    try:
        months_range_from = None
        months_range_to = None
        if range_from and range_to:
            months_range_from = range_from * 12
            months_range_to = range_to * 12
        elif range_from and (not range_to):
            months_range_from = range_from * 12
        elif range_to and (not range_from):
            months_range_to = range_to * 12
        else:
            return None
        experience_filter = build_range_query(
            field_name=field_name,
            range_from=months_range_from,
            range_to=months_range_to,
        )
        return experience_filter
    except Exception as ex:
        logger.error(f"Error while building query for 'years of experience' in {__file__}: {ex}")
        raise RuntimeError(f"Error while building query for 'years of experience': {ex}") from ex

def build_range_query_for_struct_type(
    outer_field_name: str,
    inner_field_name: str,
    range_from: float | None,
    range_to: float | None,
):
    try:
        if range_to and range_from:
            range_filter = f"(range({outer_field_name}.{inner_field_name}, {range_from}, {range_to}))"
            return range_filter
        elif range_from and not range_to:
            range_filter = (
                f"({outer_field_name}.{inner_field_name} >= {range_from})"
            )
            return range_filter
        elif range_to and not range_from:
            range_filter = (
                f"({outer_field_name}.{inner_field_name} <= {range_to})"
            )
            return range_filter
        return None
    except Exception as ex:
        logger.error(f"Error while building RANGE query for '{outer_field_name}.{inner_field_name}' in {__file__}: {ex}")
        raise RuntimeError(
            f"Error while building RANGE query for '{outer_field_name}.{inner_field_name}': {ex}"
        ) from ex

def build_query_from_list(
    field_name: str, field_data: list[str] | None, filter_type: str, condition: str = 'OR'
):
    try:
        if field_data:
            field_filter = (
                f"{field_name} {filter_type} '"
                + f"' {condition} {field_name} {filter_type} '".join(field_data)
                + "'"
            )
            return f"({field_filter})"
        return None
    except Exception as ex:
        logger.error(f"Error while building query from list for '{field_name}' in {__file__}: {ex}")
        raise RuntimeError(
            f"Error while building query from list for '{field_name}': {ex}"
        ) from ex

def build_query_from_list_of_filters(filters_with_type: dict):
    try:
        query = ""
        if "AND" in filters_with_type and filters_with_type["AND"]:
            and_filters = " AND ".join(filters_with_type.get("AND"))
            query += f"({and_filters})"
        if query == "":
            return None
        return query
    except Exception as ex:
        logger.error(f"Error while building query from list of filters in {__file__}: {ex}")
        raise RuntimeError(
            f"Error while building query from list of filters: {ex}"
        ) from ex

def build_query_for_hard_filters(filters_list: list[str]):
    try:
        filtered_query_list = [query for query in filters_list if query]
        if filtered_query_list:
            filters = {"AND": filtered_query_list}
            hard_filter_query = build_query_from_list_of_filters(
                filters
            )
            return hard_filter_query
        return None
    except Exception as ex:
        logger.error(f"Error while building query for hard filters in {__file__}: {ex}")
        raise RuntimeError(
            f"Error while building query for hard filters: {ex}"
        ) from ex
    
def build_query_for_soft_filters(query_filters_list: list[str]):
    try:
        query_filters_list = [
            query_filter
            for query_filter in query_filters_list
            if query_filter
        ]
        if query_filters_list:
            lexical_query = "({{targetHits:100}}weakAnd({}))".format(
                ",".join(query_filters_list)
            )
            logger.info(f"WeakAND query: {lexical_query}")
            return lexical_query
        return None
    except Exception as ex:
        logger.error(f"Error while building query for soft filters in {__file__}: {ex}")
        raise RuntimeError(
            f"Error while building query for soft filters: {ex}"
        ) from ex

def build_search_query(
    schema: str,
    hard_filter_query: str | None,
    soft_filter_query: str | None,
    semantic_query: str | None,
):
    try:
        base_query = f"select * from {schema} where "
        parts = []
        if hard_filter_query:
            parts.append(hard_filter_query)
        if soft_filter_query and semantic_query:
            parts.append(f"({soft_filter_query} OR {semantic_query})")
        elif soft_filter_query:
            parts.append(f"({soft_filter_query})")
        elif semantic_query:
            parts.append(f"({semantic_query})")
        filter_query = f"({' AND '.join(parts)})" if parts else None
        return f"{base_query}{filter_query}" if filter_query else None
    except Exception as ex:
        logger.error(f"Error while building query in QueryBuilder in {__file__}: {ex}")
        raise RuntimeError(
            f"Error while building query in QueryBuilder: {ex}"
        ) from ex

def get_field_presence(search_params):
    query_dict = {}
    try:
        for name, value in vars(search_params).items():
            if name in search_input_fields:
                weight = 1 if value else 0
                query_dict[f"input.query({search_input_fields.get(name)})"] = weight
        return query_dict
    except Exception as ex:
        logger.error(f"Error while getting field presence in {__file__}: {ex}")
        raise RuntimeError(f"Error while getting field presence: {ex}") from ex
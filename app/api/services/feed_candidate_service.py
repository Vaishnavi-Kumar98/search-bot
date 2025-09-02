import os
import logging
from vespa.application import Vespa
from fastapi import HTTPException

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

VESPA_FEED_URL = os.environ.get("VESPA_FEED_URL", "http://localhost:8080")

def feed_candidate_to_vespa(schema: str, data_id: str, fields: dict) -> dict:
    """
    Feed a candidate document to Vespa.
    Raises HTTPException if the feed fails.
    """
    try:
        vespa_app = Vespa(url=VESPA_FEED_URL)
        logger.info(f"Attempting to feed data_id={data_id}, schema={schema} in {__file__}")
        feed_result = vespa_app.feed_data_point(schema=schema, data_id=data_id, fields=fields)
        if not feed_result.is_successful():
            logger.error(f"Feed failed for data_id={data_id}: {feed_result.json}")
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to feed document", "vespa_response": feed_result.json}
            )
        logger.info(f"Feed successful for data_id={data_id}")
        return feed_result.json
    except Exception as ex:
        logger.error(f"Exception in {__file__} while feeding candidate: {ex}")
        raise HTTPException(
            status_code=500,
            detail={"message": f"Exception while feeding candidate: {ex}"}
        ) from ex
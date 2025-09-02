import logging
import os
import aiofiles

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.api.services.parse_candidate_service import parse_file_with_llm

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/parse_resume")
async def parse_resume(
        file_path: str
):
    logger.info(f"Starting resume parsing request for: {file_path}")
    try:
        # Parse with LLM (file is still available in temp_dir)
        result = await parse_file_with_llm(
            tmp_file_path=file_path,
        )

        logger.info(f"Resume parsing completed successfully for: {file_path}")
        return result

    except (ValueError, HTTPException) as e:
        logger.error(f"Known error occurred during resume parsing: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error occurred during resume parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
import logging

from fastapi import HTTPException

from app.api.models.builder.candidate_profile_builder import CandidateProfileBuilder
from app.api.services.gemini_service import gemini_parser_run


logger = logging.getLogger(__name__)


async def parse_file_with_llm(tmp_file_path: str) -> dict:
    """
    Parse file using LLM with retry logic.

    Args:
        tmp_file_path: Path to the file to parse
        model_name: Name of the model to use
        docx_flag: Boolean flag indicating if the file is a DOCX file

    Returns:
        Parsed profile data
    """
    logger.info(f"Starting LLM parsing for file: {tmp_file_path}")
    print("INSIDE PARSE FILE WITH LLM FUNCTION")
    try:
        # Get LLM output with retry logic
        llm_output = await gemini_parser_run(tmp_file_path)

        logger.info(f"LLM parsing completed successfully for: {tmp_file_path}")

        # Build user profile
        logger.info("Building user profile from parsed data")
        response = CandidateProfileBuilder(llm_data=llm_output)
        response_value = response.build_user_profile()

        if not response_value or not isinstance(response_value, dict):
            logger.error("Parsed profile is empty or invalid.")
            raise ValueError("Parsed profile is empty or invalid.")

        logger.info("User profile built successfully")
        return response_value

    except Exception as e:
        logger.error(f"Error occurred while parsing file with LLM: {str(e)}")
        # Raise a generic exception to be caught by the router and converted to HTTPException
        raise


class ProfileBuilderWithoutValidation:
    def __init__(self, profile_data: dict):
        self.profile_data = profile_data

    def build_user_profile(self) -> dict:
        try:
            profile = {}
            # ... build profile as before ...
            profile = {k: v for k, v in profile.items() if v is not None}
            if not profile:
                raise ValueError("Profile data is empty after building.")
            return profile
        except Exception as ex:
            logger.error(f"Error building user profile: {ex}")
            raise
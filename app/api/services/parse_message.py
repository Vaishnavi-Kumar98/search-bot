import logging
import time
import google.generativeai as genai

from app.api.services.gemini_service import get_model
from app.api.utils.json_format import JsonFormat


logger = logging.getLogger(__name__)


def parse_query(query: str):
    try:
        prompt = f"""
            You are an intent classifier and information extractor.

            Given this user input:
            "{query}"

            Step 1: Classify the intent into one of these:
            - "PARSE": if the user is asking to parse a resume/profile/document
            - "SEARCH": if the user wants to search for candidates or jobs
            - "NONE": if it's unrelated or cannot be classified

            Step 2: If intent is "SEARCH", extract parameters in **exact JSON** with this schema:
            {{
            "searchType": "lexical" | "semantic" | "both",
            "skills": [list of skills],
            "jobRole": [list of roles],
            "jobTitle": [list of job titles],
            "location": [list of locations],
            "experienceMin": int,
            "experienceMax": int,
            "expectedSalaryMin": int,
            "expectedSalaryMax": int
            }}

            Rules:
            - Do NOT hallucinate values
            - If numbers are missing, set them to 0
            - If search type is not mentioned, set "both"
            - Ensure valid JSON format only

            Return ONLY a JSON response in this format:
            {{
            "intent": "PARSE" | "SEARCH" | "NONE",
            "searchParams": null OR searchParamsObject
            }}
        """
        model = get_model()

        logger.info("Calling Gemini API for text parsing...")

        start_time = time.perf_counter()
        try:
            response = model.generate_content(prompt)
            print(response.text)
            logger.info(f"Gemini response: {response.text}")
        except Exception as ex:
            logger.error(f"Error parsing text in Gemini: {ex}")
            raise RuntimeError(f"Error parsing text in Gemini: {ex}") from ex
        end_time = time.perf_counter()
        time_taken = end_time - start_time
        logger.info(f"Time taken for parsing call: {time_taken:.4f} seconds")
        try:
            expected_data_types = {
                "intent": str,
                "searchparams": {
                    "searchtype": str,
                    "skills": [str],
                    "jobrole": [str],
                    "jobtitle": [str],
                    "location": [str],
                    "experiencemin": int,
                    "experiencemax": int,
                    "expectedsalarymin": int,
                    "expectedsalarymax": int
                }
            }
            sanitized_result = JsonFormat(expected_data_types=expected_data_types).process(response.text)
            print(sanitized_result)
        except Exception as ex:
            logger.error(f"Error processing LLM output to JSON: {ex}")
            raise RuntimeError(f"Error processing LLM output to JSON: {ex}") from ex
        
        if not sanitized_result:
            logger.error("LLM parser returned no data.")
            raise ValueError("LLM parser returned no data.")

        logger.info("Gemini parsing and sanitization successful.")
        return sanitized_result
    except Exception as ex:
        logger.error(f"LLM parser failed: {ex}")
        raise
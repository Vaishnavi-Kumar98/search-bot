import json
import logging
from typing import Any, Dict

from json_repair import repair_json
from app.api.exceptions.invalid_exception import InvalidError

logger = logging.getLogger(__name__)


class JsonFormat:
    def __init__(self, jsondata=None, expected_data_types=None) -> None:
        self.jsondata = jsondata or {}
        default_expected_data_types = {
            "name": str,
            "email": [str],
            "mobile": [str],
            "address": {
                "streetaddress": str,
                "location": str,
                "state": str,
                "pincode": str,
            },
            "dob": str,
            "gender": str,
            "maritalstatus": str,
            "skills": [str],
            "certifications": [
                {
                    "name": str,
                    "specialization": str,
                    "year": str,
                }
            ],
            "summary": str,
            "bloodgroup": str,
            "languages": [str],
            "social": [{"type": str, "url": str}],
            "hobbies": [str],
            "education": [
                {
                    "course": str,
                    "coursetype": str,
                    "specialization": str,
                    "yearofpassing": str,
                    "marksinpercentage": str,
                    "gradetype": str,
                    "institute": str,
                    "board": str,
                    "islatesteducation": bool,
                }
            ],
            "workexperience": {
                "totalyearsofexperience": float,
                "workhistory": [
                    {
                        "organisation": str,
                        "jobtitle": str,
                        "role": str,
                        "industry": str,
                        "employmenttype": str,
                        "startdate": str,
                        "enddate": str,
                        "islatest": bool,
                    }
                ],
            },
            "currentctc": float,
            "expectedctc": float
        }
        self.expected_data_types = expected_data_types if expected_data_types is not None else default_expected_data_types

    def convert_keys_to_lower(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                key.lower(): self.convert_keys_to_lower(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self.convert_keys_to_lower(item) for item in data]
        return data

    def sanitize_value(self, value: Any, expected_type: Any) -> Any:
        if isinstance(expected_type, dict):
            if isinstance(value, dict):
                return {
                    k: self.sanitize_value(value.get(k, None), t)
                    for k, t in expected_type.items()
                }
            return None

        if isinstance(expected_type, list):
            if isinstance(value, list):
                # Check the type of elements in the list
                sanitized_list = [
                    self.sanitize_value(v, expected_type[0]) for v in value
                ]
                sanitized_list = [
                    item for item in sanitized_list if item is not None
                ]  # Remove None elements
                return sanitized_list if sanitized_list else None
            return None

        if value is None or (isinstance(value, str) and value.lower() in ["null", ""]):
            return None

        if isinstance(value, expected_type):
            return value

        try:
            return expected_type(value)
        except (ValueError, TypeError):
            return None

    def sanitize_and_validate_data(self) -> Dict[str, Any]:
        sanitized_data = {}
        try:
            for field_name, expected_type in self.expected_data_types.items():
                value = self.jsondata.get(field_name, None)
                sanitized_data[field_name] = self.sanitize_value(value, expected_type)
        except Exception as ex:
            logger.error(f"Error while processing the LLM response: {ex}")
            raise InvalidError(
                error_type="ServiceError",
                error_code=500001,
                http_status_code=500,
                message=f"Service error occurred while processing the response.",
            )
        return sanitized_data

    def extract_json_from_string(self, text_with_json: str) -> dict:
        # Find the start and end positions of the JSON object
        start_index = text_with_json.find("{")
        end_index = text_with_json.rfind("}") + 1

        # Extract the JSON object from the string
        json_str = text_with_json[start_index:end_index]
        json_str = json_str.replace("\\", "")
        try:
            format_json = json.loads(json_str)
        except Exception as ex:
            print("Error while extracting json from string: ", ex)
            repair_json_str = repair_json(json_str)
            format_json = json.loads(repair_json_str)
        return format_json

    def process(self, text_with_json: str) -> dict:
        extracted_json = self.extract_json_from_string(text_with_json)
        self.jsondata = self.convert_keys_to_lower(extracted_json)
        return self.sanitize_and_validate_data()

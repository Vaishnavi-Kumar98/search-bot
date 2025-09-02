import os
import shutil
from fastapi import UploadFile
import requests

API_BASE_URL = "http://localhost:8070/profile-search"
def call_api_based_on_intent(file: UploadFile, intent_result: dict):
    intent = intent_result.get("intent")
    if intent == "PARSE":
        if file is not None:
            temp_file_path = os.path.join("/tmp", file.filename)
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            files = {"file": (file.filename, open(temp_file_path, "rb"), file.content_type or "application/pdf")}
            response = requests.post(
                f"{API_BASE_URL}/parse_resume?file_path={temp_file_path}",
                files=files,
                timeout=60
            )
            files["file"][1].close()
            if response.status_code == 200:
                result = response.json()
                feed_success, feed_error = feed_api(result)
                if feed_success:
                    print("Parsed data fed successfully to Vespa!")
                    return {"status_code": 200, "detail": "Parsed and fed successfully"}
                else:
                    print(f"Failed to feed parsed data to Vespa. Reason: {feed_error}")
                    return {"status_code": 500, "detail": f"Feed error: {feed_error}"}
            return {"status_code": response.status_code, "detail": response.text}
        else:
            return {"status_code": 404, "detail": "No file provided for parsing."}
    elif intent == "SEARCH":
        search_params = intent_result.get("searchParams")
        # Call the candidate/job search API with search_params
        pass  # Implement search logic here
    else:
        # Handle NONE or unrecognized intents
        pass  # Implement logic for NONE intent here

def feed_api(data: dict) -> tuple[bool, str]:
    """
    Calls the feed API and returns (success, error_message).
    """
    try:
        response = requests.post(f"{API_BASE_URL}/feed", json=data, timeout=10)
        if response.status_code == 200:
            return True, ""
        else:
            # Try to extract error message from response
            try:
                error_detail = response.json().get("detail", response.text)
            except Exception:
                error_detail = response.text
            return False, f"Feed API error {response.status_code}: {error_detail}"
    except Exception as ex:
        return False, f"Feed API exception: {ex}"
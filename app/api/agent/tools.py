from agno.tools import tool

from app.api.models.candidate_profile import CandidateProfile
from app.api.models.search_request import SearchRequest
from app.api.routers.feed_candidate import feed_candidate_profiles
from app.api.routers.search_candidate import search_candidate_profiles
from app.api.services.job_service import search_job
from app.api.services.parse_candidate_service import parse_file_with_llm

@tool(instructions="""
    - ** means to bold the text in markdown.
    - Take the JSON result that is received from the search_api tool, rewrite it into a natural language summary for the user.
    - Show the top 5 results only.
    - Example: If search_api returns a list of profiles, summarize it like:
    "I found N(LENGTH of the response) profiles that match your filters. These are the top 5 profiles:
      1. Match score for **<id>: <relevance_score>%**
                \\n <name> with **<experience> years of experience** in <skills>, currently a **<job_role>** residing in **<location>**."\\n
    - Do not just return the raw JSON unless explicitly asked for it.
    - Use proper line breaks and spacing for better readability.
    """
)
async def search_api(search_params: dict):
    """Call the search API with the given search params."""
    print("IM IN SEARCH API TOOL ",search_params)
    params = SearchRequest(**search_params)
    response = await search_candidate_profiles(request_body=params)
    print(len(response))
    return response

@tool(instructions="""
    - ** means to bold the text in markdown.
    - If feed is successful, return a message: "**Successfully saved** your profile **<candidate_id>** to database"
    - In the next line, Add a summary about the profile that was saved.
    - Example: Here's a short summary of your resume "<first_name> <last_name> with **<total_months_of_experience>(Instruction: convert to years) years of experience** in <skills>, currently a **<latest_job_role>** residing in **<current_city>**."
    - Also, show the top 3 jobs that has been found and give a brief summary of each job.
    - Example: "I found N jobs that match your profile. Here are the top 3 jobs:
    1. Match score: **<relevance_score>%** \\n
            **<job_title>** at **<company>** in <location> requiring <experience> years of experience with a salary of <salary>. \\n Brief description: <description> \\n
    - If no jobs found, return a message: "No matching jobs found for your profile: <candidate_id>"
    - If feed fails, return a message: "Failed to save your profile **<candidate_id>** to database. Please try again."
    - Do not just return the raw JSON unless explicitly asked for it.
    - Use proper line breaks and spacing for better readability.
    """
)
async def parse_api(file_path: str | None):
    """Call the parse_resume method with the given file if present, else return error."""
    print("IM IN PARSE API TOOL")
    if file_path is None:
        return "Error: No file provided for parsing."
    try:
        result = await parse_file_with_llm(
            tmp_file_path=str(file_path),
        )
        candidate_profile = CandidateProfile(**result)
        feed_response = await feed_candidate_profiles(candidate_profile)
        print("GOT FEED RESPONSE: ",feed_response)
        feed_success = False
        feed_message = "Failed to feed to database"
        candidate_id = result.get('id', 'Unknown')
        
        if feed_response and isinstance(feed_response, dict):
            if feed_response.get('message') == 'Document fed successfully':
                feed_success = True
                vespa_id = feed_response.get('vespa_response', {}).get('id', '')
                feed_message = f"Successfully saved candidate {candidate_id} to database (Vespa ID: {vespa_id})"
                payload= feed_response.get('vespa_payload', {})
                location = payload.get("preferred_and_current_cities")
                job_search_request = SearchRequest(
                    searchType="both",
                    searchParams={
                        "skills": payload.get("skills", []) or [],
                        "jobRole": [payload["latest_role"]] if payload.get("latest_role") else [],
                        "jobTitle": [payload["latest_job_title"]] if payload.get("latest_job_title") else [],
                        "location": location if isinstance(location, list) else [location] if location else [],
                        "experienceMin": (
                            int(payload["total_months_of_experience"]) // 12
                            if payload.get("total_months_of_experience") is not None
                            else None
                        ),
                        "expectedSalaryMin": int(payload["expected_annual_ctc"]) if payload.get("expected_annual_ctc") else None,
                    }
                )
                jobs = search_job(job_search_request)
            else:
                feed_message = f"Feed failed: {feed_response.get('message', 'Unknown error')}"
        
        # Create response with parsed details and feed status
        response = {
            "parsed_profile": result,  # Original dict for display
            "feed_status": feed_message,
            "feed_success": feed_success,
            "feed_response": feed_response,
            "jobs": jobs if feed_success else []
        }
        
        return response
    except Exception as ex:
        return f"Exception occurred while calling parse_resume: {ex}"


def apply_for_job(job_id: str, candidate_id: str):
    """Simulate applying for a job."""
    # In a real implementation, this would involve more complex logic
    return f"Applied for job {job_id} with candidate profile {candidate_id}."
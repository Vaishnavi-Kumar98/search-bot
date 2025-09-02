import json
import os
import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost:8070"

st.set_page_config(page_title="Vespa Search & Feed", layout="wide")
st.title("🔍 Candidate Feed & Search")
tab1, tab2, tab3 = st.tabs(["🔍 Search", "📥 Feed", "📄 Parse Resume"])

def feed_api(data: dict) -> tuple[bool, str]:
    """
    Calls the feed API and returns (success, error_message).
    """
    try:
        response = requests.post(f"{API_BASE_URL}/profile-search/feed", json=data, timeout=10)
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

def format_results(results: list) -> pd.DataFrame:
    rows = []
    for r in results:
        sf = r.get("summary_features", {})
        rows.append({
            "ID": r.get("id"),
            "Name": r.get("name"),
            "Email": r.get("email"),
            "Mobile": r.get("mobile_number"),
            "City": r.get("current_city"),
            "Role": r.get("job_role"),
            "Title": r.get("job_title"),
            "Experience (Months)": r.get("total_months_of_experience"),
            "Skills": ", ".join(r.get("skills", [])) if r.get("skills") else "",
            "Relevance Score": r.get("relevance_score"),
            "Latest Role Score": sf.get("latest_role_score") * 100 if sf.get("latest_role_score") is not None else None,
            "Latest Title Score": sf.get("latest_title_score") * 100 if sf.get("latest_title_score") is not None else None,
            "Skills Score": sf.get("skills_score") * 100 if sf.get("skills_score") is not None else None,
            "Created At": r.get("created_at"),
            "Created By": r.get("created_by"),
        })
    return pd.DataFrame(rows)

def build_search_payload(skills, role, title, location, exp_min, exp_max, salary_min, salary_max, search_type_value):
    return {
        "searchType": search_type_value,
        "searchParams": {
            "skills": [s.strip() for s in skills.split(",")] if skills else [],
            "jobRole": [r.strip() for r in role.split(",")] if role else [],
            "jobTitle": [t.strip() for t in title.split(",")] if title else [],
            "location": [l.strip() for l in location.split(",")] if location else [],
            "experienceMin": exp_min if exp_min else None,
            "experienceMax": exp_max if exp_max else None,
            "expectedSalaryMin": salary_min if salary_min else None,
            "expectedSalaryMax": salary_max if salary_max else None,
        }
    }

def handle_search():
    st.header("Search Candidate Profiles")
    skills = st.text_input("Skills (comma separated)")
    role = st.text_input("Job Role (comma separated)")
    title = st.text_input("Job Title (comma separated)")
    location = st.text_input("Location (comma separated)")
    exp_min = st.number_input("Minimum Experience", min_value=0, step=1)
    exp_max = st.number_input("Maximum Experience", min_value=0, step=1)
    salary_min = st.number_input("Minimum Current Salary", min_value=0, step=1000)
    salary_max = st.number_input("Maximum Current Salary", min_value=0, step=1000)
    search_type = st.radio("Search Type", ("Lexical", "Semantic", "Both"))
    search_type_map = {"Lexical": 0, "Semantic": 1, "Both": 2}
    search_type_value = search_type_map[search_type]

    if st.button("Search"):
        try:
            payload = build_search_payload(
                skills, role, title, location, exp_min, exp_max, salary_min, salary_max, search_type_value
            )
            response = requests.post(f"{API_BASE_URL}/profile-search/search", json=payload, timeout=30)
            if response.status_code == 200:
                results = response.json()
                if isinstance(results, dict) and "results" in results:
                    results = results["results"]
                if results:
                    st.subheader("📊 Candidates Table")
                    df = format_results(results)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("No results found.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as ex:
            st.error(f"Exception occurred: {ex}")

def process_feed_data(data: list) -> None:
    success_count = 0
    failed_items = []
    failed_reasons = []
    for i, item in enumerate(data, start=1):
        feed_success, feed_error = feed_api(item)
        if feed_success:
            success_count += 1
        else:
            failed_items.append(i)
            failed_reasons.append(f"Item {i}: {feed_error}")
    st.success(f"✅ Total items fed successfully: {success_count}")
    if failed_items:
        st.error(f"❌ Failed item indices: {failed_items}")
        for reason in failed_reasons:
            st.error(reason)

def handle_feed():
    st.header("Feed Data")
    uploaded_file = st.file_uploader("Upload JSON file", type="json")
    if uploaded_file is None:
        return
    try:
        data = json.load(uploaded_file)
    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid file.")
        return
    except Exception as ex:
        st.error(f"Exception occurred while reading file: {ex}")
        return

    if not isinstance(data, list):
        st.error("Uploaded JSON should be a list of objects.")
        return

    if st.button("Feed Data"):
        process_feed_data(data)

def handle_parse_resume():
    st.header("Parse Resume")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        with st.spinner("Uploading and parsing resume..."):
            try:
                # Save file to a temporary path
                temp_file_path = os.path.join("/tmp", uploaded_file.name)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                files = {"file": (uploaded_file.name, open(temp_file_path, "rb"), "application/pdf")}
                response = requests.post(
                    f"{API_BASE_URL}/profile-search/parse_resume?file_path={temp_file_path}",
                    files=files,
                    timeout=60
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success("Resume parsed successfully!")
                    st.subheader("Parsed Data")
                    st.json(result)

                    # Call the feed API with the parsed data
                    st.info("Feeding parsed data to Vespa...")
                    # feed_success, feed_error = feed_api(result)
                    # if feed_success:
                    #     st.success("Parsed data fed successfully to Vespa!")
                    # else:
                    #     st.error(f"Failed to feed parsed data to Vespa. Reason: {feed_error}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as ex:
                st.error(f"Exception occurred: {ex}")
            finally:
                # Clean up the temp file
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass

with tab1:
    handle_search()

with tab2:
    handle_feed()

with tab3:
    handle_parse_resume()
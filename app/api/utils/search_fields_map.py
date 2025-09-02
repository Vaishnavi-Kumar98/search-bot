search_input_fields = {
    "skills": "skills_weight",
    "jobTitle": "latest_job_title_weight",
    "jobRole": "latest_role_weight",
}

candidate_field_map = {
    "skills_exact":"skills_attr",
    "skills":"skills",
    "skillsEmbedding":"skills_embedding",
    "roleEmbedding":"latest_role_embedding",
    "titleEmbedding":"latest_job_title_embedding",
    "jobRole":"latest_role",
    "jobTitle":"latest_job_title",
    "location":"preferred_and_current_cities",
    "yearsOfExperience":"total_months_of_experience",
    "ctc":"expected_annual_ctc"
}

job_field_map = {
    "skills_exact":"skills",
    "skills":"skills",
    "skillsEmbedding":"skills_embedding",
    "roleEmbedding":"job_role_embedding",
    "titleEmbedding":"job_title_embedding",
    "jobRole":"job_role",
    "jobTitle":"job_title",
    "location":"location",
    "yearsOfExperience":"total_months_of_experience",
    "ctc":"annual_ctc"
}
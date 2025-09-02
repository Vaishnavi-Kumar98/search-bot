import json
import logging
import time
import os
from typing import Optional
import google.generativeai as genai
import asyncio
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from app.api.utils.json_format import JsonFormat
from langfuse.callback import CallbackHandler
from google.generativeai.types.file_types import File

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini"
CHUNK_SIZES = {
    "gemini-1.5-flash": int(128_000 * 0.8),
}

async def gemini_parser_run(file):
    """
    Calls Gemini API to parse the resume file and returns the sanitized result.
    Raises exceptions if any step fails.
    """
    try:
        output_example = {
            "name": "arun",
            "email": ["arun@gmail.com"],
            "mobile": ["9876543210"],
            "address": {
                "StreetAddress": "Flat 32, SJR Prime Apartments, Shubh Enclave",
                "Location": "Bangalore",
                "State": "Karnataka",
                "Pincode": "560060",
            },
            "DOB": "1995-03-24",
            "gender": "Male",
            "maritalStatus": "Unmarried",
            "skills": ["Java", "Springboot", "AWS Serverless", "SQL", "MongoDB"],
            "certifications": [
                {"Name": "AWS", "Specialization": "Cloud", "Year": "2021"},
                {"Name": "Azure", "Specialization": "Cloud", "Year": "2020"},
            ],
            "bloodGroup": "B+",
            "languages": ["English", "Hindi"],
            "social": [
                {"Type": "linkedIn", "URL": "https://in.linkedin.com/"},
                {"Type": "Medium", "URL": "https://medium.com/.com/"},
            ],
            "hobbies": ["Reading", "Travelling", "Music"],
            "education": [
                {
                    "Course": "B.Tech",
                    "CourseType": "Full Time",
                    "Specialization": "Computer Science",
                    "YearOfPassing": "2016",
                    "MarksInPercentage": "9.7",
                    "GradeType": "CGPA",
                    "Institute": "Amrita Institute of Technology",
                    "Board": "Biju Pattanik University of Technology",
                    "isLatestEducation": True,
                },
                {
                    "Course": "12th",
                    "CourseType": "Full Time",
                    "Specialization": "Science",
                    "YearOfPassing": "2012",
                    "MarksInPercentage": "85",
                    "GradeType": "Percentage",
                    "Institute": "G. M Junior College",
                    "Board": "CHSE",
                    "isLatestEducation": False,
                },
                {
                    "Course": "10th",
                    "CourseType": "Full Time",
                    "Specialization": "Science",
                    "YearOfPassing": "2010",
                    "MarksInPercentage": "87",
                    "GradeType": "Percentage",
                    "Institute": "College of Engineering",
                    "Board": "Odisha Board",
                    "isLatestEducation": False,
                },
            ],
            "WorkExperience": {
                "TotalYearsOfExperience": 8.5,
                "WorkHistory": [
                    {
                        "Organisation": "InfoTech",
                        "JobTitle": "Senior Software Engineer",
                        "Role": "Developer",
                        "Industry": "IT",
                        "EmploymentType": "Full time",
                        "StartDate": "2022-08-01",
                        "EndDate": "Present",
                        "isLatest": True,
                    },
                    {
                        "Organisation": "Infotech2",
                        "JobTitle": "Software engineer",
                        "Role": "Developer",
                        "Industry": "IT",
                        "EmploymentType": "Full time",
                        "StartDate": "2017-06-12",
                        "EndDate": "2022-07-23",
                        "isLatest": False,
                    },
                ],
            },
            "CurrentCTC": "15 LPA", 
            "ExpectedCTC": "20 LPA"
        }
        example = json.dumps(output_example)
        prompt = f"""You are a HR Recruiter. Parse the given file (content may have other languages apart from English) and extract the following fields in strictly valid JSON format.
            - Name
            - Email - list of emails
            - Mobile - list of mobile
            - Address with nested fields: StreetAddress, Location (city or town), State and PinCode
            - DOB: Date of Birth
            - Gender
            - MaritalStatus
            - Skills: array of skill
            - Certifications: array of items, each item with nested fields: Name, Specialization, Year
            - BloodGroup
            - CurrentCTC
            - ExpectedCTC
            - Languages: array of languages known
            - Social: array of items, each item with nested fields: Type (e.g, LinkedIn, Medium, Twitter, etc.), URL
            - Hobbies: array of hobbies (e.g, Reading, Travelling, etc.)
            - Education: array of items, each item with nested fields: Course (e.g, BTech, MSc, etc.), CourseType (Full Time, Part Time, Correspondence),Specialization (e.g, Computer Science, Electrical, etc.), YearOfPassing, MarksInPercentage, GradeType (Percentage, CGPA, etc.), Institute, Board, isLatestEducation
            - WorkExperience with nested fields: (TotalYearsOfExperience, WorkHistory with nested fields: Organisation, JobTitle, Role, Industry, EmploymentType, StartDate, EndDate, isLatest)
            
            
            Adhere to the following instructions strictly.

            For DOB:
            Generate a date of birth ('DOB') in the format 'YYYY-MM-DD' if it is present in the resume text else return None. If it is present, consider various input styles and ensure the output adheres to the standard year-month-day. The expected format should consist of four digits for the year ('YYYY'), two digits for the month ('MM'), two digits for the day ('DD') separated by hyphens ('-').

            For TotalYearsOfExperience:
            1. If total years of experience mentioned explicitly in resume, then set TotalYearsOfExperience field to be the same,  else output as null.
            2. If total months of experience is mentioned in resume, then convert it to years and months format and populate the TotalYearsOfExperience field. For example, if 20 months of experience is mentioned, then convert it to 1.6 years and populate the field.
            3. If total years of experience is not explicitly mentioned in resume, then derive it from the work history field. To derive it, first calculate the individual year of experience w.r.t each organization, then sum them up to estimate the TotalYearsOfExperience.

            For Skills:
            1. Extract explitly mentioned skills in skill section of the resume
            2. Also extract relevant skill terms present in other sections as well, excluding language skills

            For education:
            1. For course, it should contain only the degree of the course without the specialisation added to it.
            1. For coursetype, generate course type if it is present in the resume text, else return None
            2. For isLatestEducation field, consider the year of education and populate the field based on the recency of the completion
            3. For marksinpercentage, take the grade/marks corresponding to the each education details in the resume text

            For Certifications: If there is no certification mentioned in resume, then simply output "Certifications":null

            For CTC:
            1. Search the resume for any mention of salary, compensation, or CTC.
            2. If values are found:
                a.Extract both current and expected amounts (if available).
                b.Normalize values into Lakhs Per Annum (LPA), regardless of how they are written (e.g., “28,92,000”, “28.92 Lakhs”, “28.92 LPA”, “2.4M INR”, etc.).
                c.Always represent the numbers as decimal values rounded to two decimal places.

            For Social: If no social items are present then simply output "Social":null

            For Languages: Output the languages in array/list form. Don't output language proficiency level or any other information related to languages.

            Strictly adhere to the information present in resume. Do not make up anything if you do not find from resume.
            Don't include any note about how you extracted the fields. Only show the valid JSON output. Output all the nested attributes and If any information is not found, then simple put null.
            Avoid including irrelevant or excessive content. Ensure the profile accurately reflects the skills, qualifications and experiences outlined in the resume.
            
            ##OUTPUT REQUIREMENT:
            The output field values should be strictly in **English**. Please translate the field values, if the original field values is not in English.
            
            Output Example:
            {example}
            """

        model = get_model()

        logger.info("Calling Gemini API for file parsing...")

        start_time = time.perf_counter()
        try:
            uploaded_file = await asyncio.to_thread(genai.upload_file, file)
        except Exception as ex:
            logger.error(f"Error uploading file to Gemini: {ex}")
            raise RuntimeError(f"Error uploading file to Gemini: {ex}") from ex

        if isinstance(uploaded_file, File):
            logger.info(f"Gemini file upload details - Name: {uploaded_file.name}, Display name: {uploaded_file.display_name}, Mimetype: {uploaded_file.mime_type}, URI: {uploaded_file.uri}, Create Time: {uploaded_file.create_time}, Expiration time: {uploaded_file.expiration_time}, Update time: {uploaded_file.update_time}, Size in bytes: {uploaded_file.size_bytes}, Error: {uploaded_file.error}, State: {uploaded_file.state}")
        elif isinstance(uploaded_file, str):
            logger.warning(f"The upload file response from Gemini is str: {uploaded_file}")
        else:
            logger.warning("The file upload response is not of FILE type")
        end_time = time.perf_counter()
        time_taken = end_time - start_time
        logger.info(f"Time taken for uploading call: {time_taken:.4f} seconds")

        inference_start_time = time.perf_counter()
        try:
            llm_output = await asyncio.to_thread(model.generate_content, [uploaded_file, prompt])
            print("LLM OUTPUT: ", llm_output.text)
        except Exception as ex:
            logger.error(f"Error during Gemini inference: {ex}")
            raise RuntimeError(f"Error during Gemini inference: {ex}") from ex

        inference_end_time = time.perf_counter()
        inference_time_taken = inference_end_time - inference_start_time
        logger.info(f"Time taken for inference call: {inference_time_taken:.4f} seconds")

        try:
            sanitized_result = JsonFormat().process(llm_output.text)
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

def get_model():
    """Return Gemini model if GOOGLE_API_KEY is set, else raise ValueError."""
    try:
        if "GOOGLE_API_KEY" in os.environ:
            return genai.GenerativeModel("gemini-1.5-flash")
        else:
            logger.error("GOOGLE_API_KEY not found in environment. Gemini model cannot be used.")
            raise ValueError(
                "GOOGLE_API_KEY not found in environment. Gemini model cannot be used."
            )
    except Exception as ex:
        logger.error(f"Error getting Gemini model: {ex}")
        raise
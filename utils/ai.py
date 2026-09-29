import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

print("API Key Loaded:", API_KEY[:5] + "...")

client = genai.Client(api_key=API_KEY)


def analyze_resume(resume_text, job_description=""):

    if job_description.strip():
        job_section = f"""
TARGET JOB DESCRIPTION:
{job_description}

Compare the resume specifically against this job description.
"""
    else:
        job_section = """
No job description was provided.
Analyze the resume generally.
"""

    prompt = f"""
You are an expert ATS Resume Analyzer and Career Advisor.

Analyze this resume carefully.

RESUME:
{resume_text}

{job_section}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "ats_score": 0,
    "job_match_score": 0,
    "summary": "short professional summary",
    "strengths": [
        "strength 1",
        "strength 2",
        "strength 3"
    ],
    "skills": [
        "skill 1",
        "skill 2",
        "skill 3"
    ],
    "missing_skills": [
        "skill 1",
        "skill 2",
        "skill 3"
    ],
    "matched_keywords": [
        "keyword 1",
        "keyword 2",
        "keyword 3"
    ],
    "missing_keywords": [
        "keyword 1",
        "keyword 2",
        "keyword 3"
    ],
    "improvements": [
        "improvement 1",
        "improvement 2",
        "improvement 3"
    ],
    "job_roles": [
        "role 1",
        "role 2",
        "role 3"
    ],
    "career_advice": [
        "advice 1",
        "advice 2",
        "advice 3"
    ]
}}

Rules:

- ats_score must be between 0 and 100.
- job_match_score must be between 0 and 100.
- Do NOT automatically give 100.
- Be realistic.
- Do not invent experience.
- Do not invent skills.
- Base the analysis on the resume.
- If a job description is provided, calculate job_match_score based on it.
- Return JSON only.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text
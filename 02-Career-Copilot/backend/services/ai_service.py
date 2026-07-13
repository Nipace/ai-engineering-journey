import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"

def analyze_resume_with_ai(
        resume: str,
        job_description: str,
)->str:
    """Analyze a resume against a job description using Groq."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")
    client = Groq(api_key=api_key)

    prompt = f"""
    Analyze the following resume against the job description:
    Return a concise analysis containing:

    1. Overall fit
    2. Strong matching qualifications
    3. Missing or weak qualifications
    4. Resume improvement suggestions
    5. Five likely interview questions

    Do not invent experience, skills, or achievements that are not present
    in the resume.

    resume: {resume}
    job_description: {job_description}

    """
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": ("You are an experienced technical recruiter and "
                    "software engineering career coach."),
            },
            {
                "role": "user",
                "content": prompt
            }, 
        ],
        temperature = 0.2,
        max_completion_tokens= 1200 
    )
    analysis = completion.choices[0].message.content
    if not analysis:
        raise RuntimeError("The AI model returned an empty response.")

    return analysis
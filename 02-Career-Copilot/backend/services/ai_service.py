import json
import os

from dotenv import load_dotenv
from groq import Groq
from pathlib import Path
from pydantic import ValidationError


from models.analysis import ResumeAnalysis

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts/resume_analysis.txt"

def load_analysis_prompt(resume: str, job_description: str) -> str:
    """Load and populate the resume-analysis prompt template."""
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    return prompt_template.format(resume=resume, job_description=job_description)

def analyze_resume_with_ai(
        resume: str,
        job_description: str,
)->ResumeAnalysis:
    """Analyze a resume against a job description using Groq."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")
    client = Groq(api_key=api_key)

    prompt = load_analysis_prompt(resume, job_description)
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                            "You are a careful technical recruiter performing an "
                            "evidence-based resume comparison. Every positive or negative "
                            "conclusion must be supported by the supplied text. Do not infer "
                            "skills that are not present and do not overlook skills simply "
                            "because they appear in another resume section. Return only valid JSON."
                        ),
            },
            {
                "role": "user",
                "content": prompt
            }, 
        ],
        temperature = 0.1,
        max_completion_tokens= 1200,
        response_format={"type": "json_object"} 
    )
    raw_content = completion.choices[0].message.content
    if not raw_content:
        raise RuntimeError("The AI model returned an empty response.")
    try:
        parsed_content = json.loads(raw_content)
        return ResumeAnalysis.model_validate(parsed_content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("The AI model returned an invalid response.") from exc
    except ValidationError as exc:
        raise RuntimeError("The AI response did not match the expected structure.") from exc
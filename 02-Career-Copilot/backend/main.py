from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title= "Career Copilot API",
    description= "Analyze a resume against a job description.",
    version= "0.0.1"
)

class AnalyzeRequest(BaseModel):
    resume: str = Field(..., min_length=20, description="The resume to analyze.")
    job_description: str = Field(..., min_length=20, description="The job description to analyze against.")
    

@app.get("/")
async def health_check() -> dict[str, str]:
    return {
        "message": "Career Copilot API is running",
        "status": "healthy"
        }
@app.post("/analyze")
def analyze_application(request: AnalyzeRequest) -> dict[str, str | int]:
    return {
        "status": "received",
        "resume_length": len(request.resume),
        "job_description_length": len(request.job_description)
        }
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from models.analysis import AnalyzeResponse

from services.pdf_parser import extract_text_from_pdf
from services.ai_service import analyze_resume_with_ai


app = FastAPI(
    title= "Career Copilot API",
    description= "Analyze a resume against a job description.",
    version= "0.0.1"
)

class AnalyzeRequest(BaseModel):
    resume: str = Field(..., min_length=20, description="The resume to analyze.")
    job_description: str = Field(..., min_length=20, description="The job description to analyze against.")
    
# class AnalyzeResponse(BaseModel):
#     status: str
#     analysis: str

@app.get("/")
async def health_check() -> dict[str, str]:
    return {
        "message": "Career Copilot API is running",
        "status": "healthy"
        }
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_application(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        analysis = analyze_resume_with_ai(request.resume, request.job_description)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=exc.args[0],
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI service is currently unavailable.",
        ) from exc
    
    return AnalyzeResponse(
        status="completed",
        analysis=analysis,
    )

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...))-> dict[str, str | int]:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a PDF file.")
    
    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file content. Please upload a valid PDF file.")
    try:
        extracted_text, page_count = extract_text_from_pdf(file_content)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to read the uploaded PDF"
        )
    if not extracted_text:
        raise HTTPException(
            status_code=422,
            detail="No readable text was found in the PDF.",
        )
    return {
            "filename": file.filename or "resume.pdf",
            "pages": page_count,
            "text": extracted_text,
        }
@app.post("/analyze-resume", response_model=AnalyzeResponse)
async def analyze_uploaded_resume(
    job_description: str = Form(...),
    file: UploadFile = File(...),
)->AnalyzeResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        ) 
    file_content = await file.read()
    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )
    try:
        resume_text, page_count = extract_text_from_pdf(file_content)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to read the uploaded PDF.",
        ) from exc    
    if not resume_text:
        raise HTTPException(
            status_code=422,
            detail="No readable text was found in the PDF.",
        )
    try:
        analysis = analyze_resume_with_ai(
            resume=resume_text,
            job_description=job_description,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI analysis service is unavailable.",
        ) from exc

    return AnalyzeResponse(
        status="completed",
        filename=file.filename or "resume.pdf",
        pages=page_count,
        analysis=analysis,
    )
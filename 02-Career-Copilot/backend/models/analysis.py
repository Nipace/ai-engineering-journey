from typing import Literal

from pydantic import BaseModel, Field


class QualificationMatch(BaseModel):
    qualification: str = Field(
        description="A job qualification matched by the resume."
    )
    evidence: str = Field(
        description="Specific evidence copied or closely paraphrased from the resume."
    )


class QualificationGap(BaseModel):
    qualification: str = Field(
        description="An important job requirement not clearly demonstrated."
    )
    reason: str = Field(
        description="Why the resume does not sufficiently demonstrate it."
    )


class ResumeAnalysis(BaseModel):
    fit_level: Literal["strong", "moderate", "weak"]

    overall_fit: str = Field(
        description="A concise explanation of the candidate's fit."
    )

    matched_qualifications: list[QualificationMatch]

    missing_qualifications: list[QualificationGap]

    recommendations: list[str]

    interview_questions: list[str]


class AnalyzeResponse(BaseModel):
    status: str
    filename: str
    pages: int
    analysis: ResumeAnalysis
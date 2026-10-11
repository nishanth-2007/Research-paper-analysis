from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SupportingExcerpt(BaseModel):
    excerpt: str
    section: Optional[str] = None
    page: Optional[int] = None


class AcademicCriterionAssessment(BaseModel):
    criterion: str  # e.g., 'novelty', 'research_question', 'methodology', etc.
    assessment: str  # 'strong', 'adequate', 'weak', 'needs_revision'
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    supporting_excerpts: List[SupportingExcerpt] = Field(default_factory=list)
    relevant_sources: List[str] = Field(default_factory=list)
    recommended_action: str
    limitations: str


class LLMAcademicEvaluationOutput(BaseModel):
    assessments: List[AcademicCriterionAssessment]
    overall_strengths: List[str] = Field(default_factory=list)
    critical_deficiencies: List[str] = Field(default_factory=list)
    preliminary_notice: str = (
        "Academic evaluation constitutes an automated advisory review. "
        "Novelty assessments are preliminary and do not substitute for formal peer review or comprehensive prior art clearance."
    )

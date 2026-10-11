from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DeductionDetail(BaseModel):
    rule_id: str
    severity: str
    points_deducted: float
    reason: str


class CategoryScoreDetail(BaseModel):
    category_id: str
    category_label: str
    score: float = Field(ge=0.0, le=100.0)
    weight: float = Field(ge=0.0, le=1.0)
    weighted_score: float
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0
    unverified_count: int = 0
    is_provisional: bool = False
    deductions: List[DeductionDetail] = Field(default_factory=list)


class EngineScoreDetail(BaseModel):
    engine_id: str  # deterministic, rag_knowledge, llm_academic
    engine_name: str
    score: float = Field(ge=0.0, le=100.0)
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0
    unverified_count: int = 0
    is_provisional: bool = False
    weight: float = 0.33


class SectionScoreDetail(BaseModel):
    section_id: str  # abstract, introduction, methodology, results, conclusion, references
    section_name: str
    score: float = Field(ge=0.0, le=100.0)
    status: str = "pass"  # pass, needs_revision, incomplete, unverified
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0
    has_sufficient_evidence: bool = True
    evidence_notes: Optional[str] = None


class ScoreCalculationBreakdown(BaseModel):
    category_scores: Dict[str, CategoryScoreDetail]
    critical_penalty_applied: float = 0.0
    formula_explanation: str


class ReadinessScoreResponse(BaseModel):
    overall_score: float = Field(ge=0.0, le=100.0)
    readiness_tier: str  # 'Ready for Submission', 'Minor Revisions', 'Major Revisions', 'Early Draft'
    is_provisional: bool = False
    provisional_reason: Optional[str] = None
    category_scores: Dict[str, CategoryScoreDetail]
    engine_scores: Dict[str, EngineScoreDetail] = Field(default_factory=dict)
    section_scores: Dict[str, SectionScoreDetail] = Field(default_factory=dict)
    critical_issues_count: int
    warnings_count: int
    unverified_count: int
    breakdown: ScoreCalculationBreakdown
    disclaimer: str = (
        "The readiness score is a deterministic indicator of structural guideline compliance and manuscript readiness. "
        "It does NOT represent a probability of acceptance by the journal editorial board."
    )

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common import Finding, SourceLocation
from app.schemas.scoring import ReadinessScoreResponse
from app.schemas.academic import AcademicCriterionAssessment


class ExecutiveSummary(BaseModel):
    manuscript_title: str
    target_journal: Optional[str] = None
    overall_score: float
    readiness_tier: str
    key_strengths: List[str] = Field(default_factory=list)
    critical_deficits: List[str] = Field(default_factory=list)
    synthesis: str


class ActionableRecommendation(BaseModel):
    priority_rank: int
    rule_id: str
    category: str
    severity: str
    title: str
    action_item: str
    estimated_impact: str
    source_location: Optional[SourceLocation] = None


class VerificationLimitation(BaseModel):
    engine: str
    scope: str
    reason: str
    guidance: str


from app.services.scoring.deduplicator import ConsolidatedIssue, VerificationCoverage


class CompleteAnalysisReport(BaseModel):
    analysis_id: str
    manuscript_id: str
    version_id: str
    manuscript_title: str
    target_journal_id: Optional[str] = None
    target_journal_name: Optional[str] = None
    guideline_version_tag: Optional[str] = None
    generated_at: datetime
    document_validation: Optional[Dict[str, Any]] = None
    verification_coverage: Optional[VerificationCoverage] = None
    consolidated_issues: List[ConsolidatedIssue] = Field(default_factory=list)
    executive_summary: ExecutiveSummary
    readiness_score: ReadinessScoreResponse
    all_findings: List[Finding] = Field(default_factory=list)
    critical_issues: List[Finding] = Field(default_factory=list)
    warnings: List[Finding] = Field(default_factory=list)
    unverified_checks: List[Finding] = Field(default_factory=list)
    actionable_recommendations: List[ActionableRecommendation] = Field(default_factory=list)
    academic_assessments: List[AcademicCriterionAssessment] = Field(default_factory=list)
    limitations: List[VerificationLimitation] = Field(default_factory=list)

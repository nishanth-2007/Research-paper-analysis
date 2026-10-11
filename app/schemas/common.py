import uuid
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    UNABLE_TO_VERIFY = "unable_to_verify"


class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"
    INFO = "info"


class EngineType(str, Enum):
    DETERMINISTIC = "deterministic"
    RAG_KNOWLEDGE = "rag_knowledge"
    LLM_ACADEMIC = "llm_academic"


class SourceLocation(BaseModel):
    page_number: Optional[int] = None
    section_name: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    snippet: Optional[str] = None


class GuidelineSource(BaseModel):
    publisher: Optional[str] = None
    guideline_name: Optional[str] = None
    section_title: Optional[str] = None
    source_url: Optional[str] = None
    verified_on: Optional[str] = None


class Finding(BaseModel):
    """
    Standardized finding schema shared by all evaluation engines.
    """
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    engine: EngineType
    category: str  # e.g., 'citations', 'sections', 'formatting', 'methodology', 'novelty'
    status: CheckStatus
    severity: Severity
    title: str
    expected_requirement: str
    actual_observation: str
    evidence: Optional[str] = None
    source_location: Optional[SourceLocation] = None
    guideline_source: Optional[GuidelineSource] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    suggested_correction: Optional[str] = None
    is_provisional: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EngineResult(BaseModel):
    """
    Standard envelope returned by every verification engine.
    """
    engine: EngineType
    execution_time_ms: float
    status: str = "completed"  # completed, partial_failure, failed
    findings: List[Finding] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

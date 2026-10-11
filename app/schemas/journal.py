from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class JournalRuleSchema(BaseModel):
    id: str
    rule_code: str
    category: str
    requirement_description: str
    rule_parameters: Optional[Dict[str, Any]] = None
    severity: str

    model_config = {"from_attributes": True}


class GuidelineChunkSchema(BaseModel):
    id: str
    chunk_index: int
    section_heading: Optional[str] = None
    content: str
    source_url: Optional[str] = None

    model_config = {"from_attributes": True}


class GuidelineVersionSchema(BaseModel):
    id: str
    journal_id: str
    version_tag: str
    effective_date: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    provenance: Optional[Dict[str, Any]] = None
    is_current: bool
    rules: List[JournalRuleSchema] = Field(default_factory=list)
    chunks: List[GuidelineChunkSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class JournalSummary(BaseModel):
    id: str
    name: str
    publisher: str
    scope: Optional[List[str]] = None
    citation_style: Optional[str] = None
    official_url: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class JournalDetail(JournalSummary):
    guideline_versions: List[GuidelineVersionSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    journal_id: Optional[str] = Field(None, description="Target journal slug (e.g. 'ieee-access', 'nature-comms')")
    include_academic_evaluation: bool = True
    config_overrides: Optional[Dict[str, Any]] = None


class AnalysisJobQueuedResponse(BaseModel):
    analysis_id: str
    manuscript_id: str
    version_id: str
    journal_id: Optional[str] = None
    status: str
    progress_percent: int
    current_step: str
    status_url: str
    message: str = "Analysis job queued successfully."


class AnalysisJobStatusResponse(BaseModel):
    analysis_id: str
    manuscript_id: str
    version_id: str
    journal_id: Optional[str] = None
    status: str  # queued, processing, completed, failed
    progress_percent: int
    current_step: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class ExportFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"


class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(min_length=6)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

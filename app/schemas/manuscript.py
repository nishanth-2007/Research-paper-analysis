from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentSectionSchema(BaseModel):
    id: Optional[str] = None
    section_order: int
    title: str
    normalized_title: str
    content: str
    word_count: int
    start_page: Optional[int] = None
    end_page: Optional[int] = None


class ReferenceSchema(BaseModel):
    id: Optional[str] = None
    reference_index: int
    raw_text: str
    detected_authors: Optional[List[str]] = None
    detected_title: Optional[str] = None
    detected_year: Optional[str] = None
    detected_doi: Optional[str] = None
    is_malformed: bool = False


class CitationSchema(BaseModel):
    id: Optional[str] = None
    citation_key: str
    context_snippet: Optional[str] = None
    page_number: Optional[int] = None
    matched_reference_id: Optional[str] = None


class ManuscriptVersionDetail(BaseModel):
    id: str
    manuscript_id: str
    version_number: int
    original_filename: str
    file_type: str
    file_size_bytes: int
    file_hash_sha256: str
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    is_scanned_pdf: bool = False
    ocr_required: bool = False
    extraction_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    sections: List[DocumentSectionSchema] = Field(default_factory=list)
    references: List[ReferenceSchema] = Field(default_factory=list)
    citations: List[CitationSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ManuscriptListItem(BaseModel):
    id: str
    title: str
    latest_version_number: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ManuscriptDetail(BaseModel):
    id: str
    title: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    versions: List[ManuscriptVersionDetail] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class UploadManuscriptResponse(BaseModel):
    manuscript_id: str
    version_id: str
    version_number: int
    title: str
    original_filename: str
    file_size_bytes: int
    file_hash_sha256: str
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    is_scanned_pdf: bool = False
    ocr_required: bool = False
    message: str = "Manuscript successfully ingested and parsed."

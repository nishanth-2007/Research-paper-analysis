import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON, Integer, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Manuscript(Base):
    __tablename__ = "manuscripts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="manuscripts")
    versions = relationship("ManuscriptVersion", back_populates="manuscript", cascade="all, delete-orphan")


class ManuscriptVersion(Base):
    __tablename__ = "manuscript_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    manuscript_id = Column(String(36), ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, default=1, nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # .pdf or .docx
    file_size_bytes = Column(Integer, nullable=False)
    file_hash_sha256 = Column(String(64), nullable=False, index=True)
    storage_path = Column(String(500), nullable=False)
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    is_scanned_pdf = Column(Boolean, default=False, nullable=False)
    ocr_required = Column(Boolean, default=False, nullable=False)
    extraction_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    manuscript = relationship("Manuscript", back_populates="versions")
    sections = relationship("DocumentSection", back_populates="version", cascade="all, delete-orphan")
    references = relationship("Reference", back_populates="version", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="version", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="manuscript_version", cascade="all, delete-orphan")


class DocumentSection(Base):
    __tablename__ = "document_sections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    manuscript_version_id = Column(String(36), ForeignKey("manuscript_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    section_order = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    normalized_title = Column(String(100), nullable=False, index=True)  # abstract, introduction, methodology, etc.
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    start_page = Column(Integer, nullable=True)
    end_page = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    version = relationship("ManuscriptVersion", back_populates="sections")


class Reference(Base):
    __tablename__ = "references"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    manuscript_version_id = Column(String(36), ForeignKey("manuscript_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_index = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=False)
    detected_authors = Column(JSON, nullable=True)
    detected_title = Column(Text, nullable=True)
    detected_year = Column(String(20), nullable=True)
    detected_doi = Column(String(100), nullable=True)
    is_malformed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    version = relationship("ManuscriptVersion", back_populates="references")
    citations = relationship("Citation", back_populates="matched_reference")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    manuscript_version_id = Column(String(36), ForeignKey("manuscript_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    citation_key = Column(String(100), nullable=False, index=True)  # e.g., "[1]" or "(Smith, 2021)"
    context_snippet = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    matched_reference_id = Column(String(36), ForeignKey("references.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    version = relationship("ManuscriptVersion", back_populates="citations")
    matched_reference = relationship("Reference", back_populates="citations")

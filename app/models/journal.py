import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class Journal(Base):
    __tablename__ = "journals"

    id = Column(String(100), primary_key=True)  # slug or standard identifier, e.g., 'ieee-access'
    name = Column(String(255), nullable=False, index=True)
    publisher = Column(String(255), nullable=False, index=True)
    scope = Column(JSON, nullable=True)  # list of scope domains
    official_url = Column(String(500), nullable=True)
    citation_style = Column(String(100), nullable=True)  # e.g. IEEE, APA7, Nature
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    guideline_versions = relationship("GuidelineVersion", back_populates="journal", cascade="all, delete-orphan")


class GuidelineVersion(Base):
    __tablename__ = "guideline_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journal_id = Column(String(100), ForeignKey("journals.id", ondelete="CASCADE"), nullable=False, index=True)
    version_tag = Column(String(50), nullable=False)
    effective_date = Column(DateTime, nullable=True)
    last_verified_at = Column(DateTime, nullable=True)
    provenance = Column(JSON, nullable=True)  # details on official source verification
    is_current = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    journal = relationship("Journal", back_populates="guideline_versions")
    rules = relationship("JournalRule", back_populates="guideline_version", cascade="all, delete-orphan")
    chunks = relationship("GuidelineChunk", back_populates="guideline_version", cascade="all, delete-orphan")


class JournalRule(Base):
    __tablename__ = "journal_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    guideline_version_id = Column(String(36), ForeignKey("guideline_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_code = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # sections, citations, layout, metadata
    requirement_description = Column(Text, nullable=False)
    rule_parameters = Column(JSON, nullable=True)  # e.g., {"max_words": 250, "min_words": 150}
    severity = Column(String(20), default="major", nullable=False)  # critical, major, moderate, minor, info
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    guideline_version = relationship("GuidelineVersion", back_populates="rules")


class GuidelineChunk(Base):
    __tablename__ = "guideline_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    guideline_version_id = Column(String(36), ForeignKey("guideline_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    section_heading = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    embedding = Column(JSON, nullable=True)  # Store vector array (compatible with sqlite and postgres json/pgvector)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    guideline_version = relationship("GuidelineVersion", back_populates="chunks")

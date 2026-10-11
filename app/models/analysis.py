import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON, Integer, Float
from sqlalchemy.orm import relationship
from app.database import Base


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    manuscript_version_id = Column(String(36), ForeignKey("manuscript_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    guideline_version_id = Column(String(36), ForeignKey("guideline_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="queued", nullable=False, index=True)  # queued, processing, completed, failed
    progress_percent = Column(Integer, default=0, nullable=False)
    current_step = Column(String(100), default="Initialized", nullable=False)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    manuscript_version = relationship("ManuscriptVersion", back_populates="analysis_jobs")
    runs = relationship("AnalysisRun", back_populates="job", cascade="all, delete-orphan")
    readiness_score = relationship("ReadinessScore", back_populates="job", uselist=False, cascade="all, delete-orphan")
    report = relationship("GeneratedReport", back_populates="job", uselist=False, cascade="all, delete-orphan")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    engine_type = Column(String(50), nullable=False, index=True)  # deterministic, rag_knowledge, llm_academic
    status = Column(String(20), default="completed", nullable=False)  # completed, failed, skipped
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    config_snapshot = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    job = relationship("AnalysisJob", back_populates="runs")
    verification_results = relationship("VerificationResult", back_populates="run", cascade="all, delete-orphan")
    academic_assessments = relationship("AcademicAssessment", back_populates="run", cascade="all, delete-orphan")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_run_id = Column(String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    status = Column(String(30), nullable=False)  # pass, fail, warning, unable_to_verify
    severity = Column(String(20), nullable=False)  # critical, major, moderate, minor, info
    expected_requirement = Column(Text, nullable=False)
    actual_observation = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    source_location = Column(JSON, nullable=True)  # {page: 1, section: "Intro", line_range: [10, 20]}
    suggested_correction = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)
    is_provisional = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    run = relationship("AnalysisRun", back_populates="verification_results")


class AcademicAssessment(Base):
    __tablename__ = "academic_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_run_id = Column(String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion = Column(String(100), nullable=False, index=True)  # novelty, methodology, consistency, etc.
    assessment_grade = Column(String(50), nullable=False)  # strong, adequate, weak, needs_revision
    confidence = Column(Float, default=0.8, nullable=False)
    explanation = Column(Text, nullable=False)
    supporting_excerpts = Column(JSON, nullable=True)
    recommended_action = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    run = relationship("AnalysisRun", back_populates="academic_assessments")


class ReadinessScore(Base):
    __tablename__ = "readiness_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    overall_score = Column(Float, nullable=False)
    is_provisional = Column(Boolean, default=False, nullable=False)
    category_scores = Column(JSON, nullable=False)  # { category: { score: 85, weight: 0.2, ... } }
    critical_issues_count = Column(Integer, default=0, nullable=False)
    warnings_count = Column(Integer, default=0, nullable=False)
    unverified_count = Column(Integer, default=0, nullable=False)
    calculation_breakdown = Column(JSON, nullable=False)
    scoring_config_snapshot = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    job = relationship("AnalysisJob", back_populates="readiness_score")


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    report_json = Column(JSON, nullable=False)
    pdf_storage_path = Column(String(500), nullable=True)
    docx_storage_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    job = relationship("AnalysisJob", back_populates="report")

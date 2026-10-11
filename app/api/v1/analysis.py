from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.manuscript import Manuscript, ManuscriptVersion
from app.models.journal import Journal, GuidelineVersion
from app.models.analysis import AnalysisJob, AnalysisRun, VerificationResult, GeneratedReport
from app.schemas.api import (
    AnalyzeRequest,
    AnalysisJobQueuedResponse,
    AnalysisJobStatusResponse,
    ExportFormat,
)
from app.schemas.report import CompleteAnalysisReport
from app.api.deps import get_current_user
from app.services.orchestrator.queue import enqueue_analysis_job
from app.services.orchestrator.runner import AnalysisOrchestrator
from app.services.storage import get_storage_service
from app.api.v1.journals import ensure_journals_seeded

router = APIRouter(tags=["Manuscript Analysis & Verification"])


@router.post("/manuscripts/{manuscript_id}/analyze", response_model=AnalysisJobQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
def analyze_manuscript(
    manuscript_id: str,
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Queue an asynchronous manuscript verification and journal readiness analysis.
    Returns HTTP 202 with analysis job tracking metadata and status URL.
    """
    ensure_journals_seeded(db)

    # 1. Fetch manuscript and latest version
    manuscript = (
        db.query(Manuscript)
        .filter(Manuscript.id == manuscript_id, Manuscript.user_id == current_user.id)
        .first()
    )
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manuscript '{manuscript_id}' not found.",
        )

    latest_version = (
        db.query(ManuscriptVersion)
        .filter(ManuscriptVersion.manuscript_id == manuscript.id)
        .order_by(ManuscriptVersion.version_number.desc())
        .first()
    )
    if not latest_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manuscript has no uploaded versions.",
        )

    # 2. Resolve journal guideline version if journal_id passed
    guideline_version_id = None
    if request.journal_id:
        gv = (
            db.query(GuidelineVersion)
            .filter(GuidelineVersion.journal_id == request.journal_id, GuidelineVersion.is_current == True)
            .first()
        )
        if not gv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target journal '{request.journal_id}' not found or has no active guideline version.",
            )
        guideline_version_id = gv.id

    # 3. Create AnalysisJob
    job = AnalysisJob(
        manuscript_version_id=latest_version.id,
        guideline_version_id=guideline_version_id,
        user_id=current_user.id,
        status="queued",
        progress_percent=0,
        current_step="Queued for analysis",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 4. Trigger asynchronous job runner
    enqueue_analysis_job(job.id)

    status_url = f"/api/v1/analysis/{job.id}"

    return AnalysisJobQueuedResponse(
        analysis_id=job.id,
        manuscript_id=manuscript.id,
        version_id=latest_version.id,
        journal_id=request.journal_id,
        status=job.status,
        progress_percent=job.progress_percent,
        current_step=job.current_step,
        status_url=status_url,
    )


@router.get("/analysis/{analysis_id}", response_model=AnalysisJobStatusResponse)
def get_analysis_status(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check analysis job processing status and progress percentage."""
    job = (
        db.query(AnalysisJob)
        .filter(AnalysisJob.id == analysis_id, AnalysisJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis job '{analysis_id}' not found.",
        )

    journal_id = job.manuscript_version.manuscript_id  # fallback
    if job.guideline_version_id and job.manuscript_version:
        gv = db.query(GuidelineVersion).filter(GuidelineVersion.id == job.guideline_version_id).first()
        if gv:
            journal_id = gv.journal_id

    return AnalysisJobStatusResponse(
        analysis_id=job.id,
        manuscript_id=job.manuscript_version.manuscript_id,
        version_id=job.manuscript_version_id,
        journal_id=journal_id,
        status=job.status,
        progress_percent=job.progress_percent,
        current_step=job.current_step,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
    )


@router.get("/analysis/{analysis_id}/results")
def get_analysis_results(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve raw engine execution results and individual findings."""
    job = (
        db.query(AnalysisJob)
        .filter(AnalysisJob.id == analysis_id, AnalysisJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis job '{analysis_id}' not found.",
        )

    runs = db.query(AnalysisRun).filter(AnalysisRun.job_id == job.id).all()
    results = []
    for r in runs:
        findings = [
            {
                "rule_id": f.rule_id,
                "category": f.category,
                "status": f.status,
                "severity": f.severity,
                "expected": f.expected_requirement,
                "observed": f.actual_observation,
                "evidence": f.evidence,
                "location": f.source_location,
                "correction": f.suggested_correction,
                "confidence": f.confidence,
                "provisional": f.is_provisional,
            }
            for f in r.verification_results
        ]
        results.append({
            "run_id": r.id,
            "engine": r.engine_type,
            "status": r.status,
            "execution_time_ms": r.execution_time_ms,
            "summary": r.config_snapshot,
            "findings": findings,
        })

    return {
        "analysis_id": job.id,
        "job_status": job.status,
        "runs": results,
    }


@router.get("/analysis/{analysis_id}/report", response_model=CompleteAnalysisReport)
def get_analysis_report(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the aggregated, explainable readiness report with category breakdown."""
    job = (
        db.query(AnalysisJob)
        .filter(AnalysisJob.id == analysis_id, AnalysisJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis job '{analysis_id}' not found.",
        )

    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Analysis job is currently '{job.status}' (progress: {job.progress_percent}%). Report is not yet ready.",
        )

    gen_report = db.query(GeneratedReport).filter(GeneratedReport.job_id == job.id).first()
    if not gen_report or not gen_report.report_json:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated report record not found for completed job.",
        )

    report_dict = dict(gen_report.report_json)

    from app.services.scoring.deduplicator import IssueDeduplicator
    from app.schemas.common import Finding
    all_findings_objs = [Finding.model_validate(f) for f in report_dict.get("all_findings", [])]

    if "consolidated_issues" not in report_dict or not report_dict["consolidated_issues"]:
        report_dict["consolidated_issues"] = [
            c.model_dump(mode="json") for c in IssueDeduplicator.consolidate_findings(all_findings_objs)
        ]

    if "verification_coverage" not in report_dict or not report_dict["verification_coverage"]:
        report_dict["verification_coverage"] = IssueDeduplicator.calculate_coverage(all_findings_objs).model_dump(mode="json")

    if "actionable_recommendations" in report_dict:
        norm_recs = []
        for r in report_dict["actionable_recommendations"]:
            r_copy = dict(r)
            imp = str(r_copy.get("estimated_impact", ""))
            if imp and "recover" not in imp.lower() and "gain" not in imp.lower():
                r_copy["estimated_impact"] = f"Fix to recover {imp}".strip()
            norm_recs.append(r_copy)
        report_dict["actionable_recommendations"] = norm_recs

    return CompleteAnalysisReport.model_validate(report_dict)


@router.get("/analysis/{analysis_id}/export")
def export_analysis_report(
    analysis_id: str,
    format: ExportFormat = Query(ExportFormat.PDF, description="Export format: pdf or docx"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the official verification and journal readiness report as PDF or DOCX."""
    job = (
        db.query(AnalysisJob)
        .filter(AnalysisJob.id == analysis_id, AnalysisJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis job '{analysis_id}' not found.",
        )

    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Analysis job is '{job.status}'. Export is available once analysis reaches 100%.",
        )

    gen_report = db.query(GeneratedReport).filter(GeneratedReport.job_id == job.id).first()
    if not gen_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exported report files not found.",
        )

    storage = get_storage_service()

    if format == ExportFormat.PDF:
        if not gen_report.pdf_storage_path or not storage.file_exists(gen_report.pdf_storage_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF export file not found.")
        file_bytes = storage.get_file(gen_report.pdf_storage_path)
        media_type = "application/pdf"
        filename = f"readiness_report_{analysis_id}.pdf"
    else:  # DOCX
        if not gen_report.docx_storage_path or not storage.file_exists(gen_report.docx_storage_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DOCX export file not found.")
        file_bytes = storage.get_file(gen_report.docx_storage_path)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"readiness_report_{analysis_id}.docx"

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

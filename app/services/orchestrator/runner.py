import time
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from app.models.manuscript import ManuscriptVersion
from app.models.journal import Journal, GuidelineVersion
from app.models.analysis import (
    AnalysisJob,
    AnalysisRun,
    VerificationResult,
    AcademicAssessment,
    ReadinessScore,
    GeneratedReport,
)
from app.schemas.common import Finding, EngineResult, EngineType
from app.services.storage import get_storage_service
from app.services.ingestion.extractor import DocumentExtractor, ExtractedDocument
from app.services.engines.deterministic import DeterministicEngine
from app.services.engines.rag import RAGEngine
from app.services.engines.academic import AcademicLLMEngine
from app.services.scoring.engine import ReadinessScoringEngine
from app.services.export.generator import ReportGenerator

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    @classmethod
    def execute_analysis(
        cls,
        db: Session,
        job_id: str,
    ) -> AnalysisJob:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            raise ValueError(f"Analysis job not found: {job_id}")

        job.status = "processing"
        job.progress_percent = 5
        job.current_step = "Loading manuscript and guideline configuration"
        db.commit()

        try:
            # 1. Load Manuscript Version & Guidelines
            version: ManuscriptVersion = job.manuscript_version
            storage = get_storage_service()

            file_bytes = storage.get_file(version.storage_path)
            extracted_doc = DocumentExtractor.extract_document(
                content=file_bytes,
                filename=version.original_filename,
            )

            guideline_version: Optional[GuidelineVersion] = None
            if job.guideline_version_id:
                guideline_version = db.query(GuidelineVersion).filter(
                    GuidelineVersion.id == job.guideline_version_id
                ).first()

            all_findings: List[Finding] = []
            engine_runs_data: List[Dict[str, Any]] = []

            # 2. Deterministic Verification Engine
            job.progress_percent = 25
            job.current_step = "Executing deterministic verification rules"
            db.commit()

            det_engine = DeterministicEngine()
            det_result = det_engine.evaluate(document=extracted_doc, guideline_version=guideline_version)
            all_findings.extend(det_result.findings)
            engine_runs_data.append({"type": EngineType.DETERMINISTIC, "result": det_result})

            # 3. Journal Knowledge Base and RAG Engine
            job.progress_percent = 50
            job.current_step = "Retrieving journal guidelines and semantic context"
            db.commit()

            rag_engine = RAGEngine()
            rag_result = rag_engine.evaluate(document=extracted_doc, guideline_version=guideline_version)
            all_findings.extend(rag_result.findings)
            engine_runs_data.append({"type": EngineType.RAG_KNOWLEDGE, "result": rag_result})

            # 4. LLM Academic Evaluation Engine
            job.progress_percent = 70
            job.current_step = "Conducting academic quality and methodological evaluation"
            db.commit()

            llm_engine = AcademicLLMEngine()
            llm_result = llm_engine.evaluate(document=extracted_doc, guideline_version=guideline_version)
            all_findings.extend(llm_result.findings)
            engine_runs_data.append({"type": EngineType.LLM_ACADEMIC, "result": llm_result})

            # 5. Deduplicate overlapping findings
            job.progress_percent = 85
            job.current_step = "Deduplicating findings and calculating readiness score"
            db.commit()

            deduplicated_findings = cls._deduplicate_findings(all_findings)

            # 6. Readiness Scoring
            readiness_score_resp = ReadinessScoringEngine.calculate_readiness_score(deduplicated_findings)

            # 7. Report Generation & Document Export
            job.progress_percent = 92
            job.current_step = "Synthesizing executive report and generating PDF/DOCX artifacts"
            db.commit()

            target_journal_id = guideline_version.journal_id if guideline_version else None
            target_journal_name = guideline_version.journal.name if (guideline_version and guideline_version.journal) else None
            guideline_tag = guideline_version.version_tag if guideline_version else None

            complete_report = ReportGenerator.build_report(
                analysis_id=job.id,
                manuscript_id=version.manuscript_id,
                version_id=version.id,
                manuscript_title=version.manuscript.title,
                findings=deduplicated_findings,
                readiness_score=readiness_score_resp,
                journal_id=target_journal_id,
                journal_name=target_journal_name,
                guideline_version_tag=guideline_tag,
                document_validation=extracted_doc.validation.model_dump() if hasattr(extracted_doc, "validation") and extracted_doc.validation else None,
            )

            # Export files
            export_paths = ReportGenerator.export_and_store_report_files(complete_report)

            # 8. Persist results in Database
            cls._persist_analysis_results(
                db=db,
                job=job,
                engine_runs_data=engine_runs_data,
                readiness_score_resp=readiness_score_resp,
                complete_report=complete_report,
                export_paths=export_paths,
            )

            job.status = "completed"
            job.progress_percent = 100
            job.current_step = "Analysis completed successfully"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

            return job

        except Exception as e:
            logger.error(f"Orchestrator pipeline failed for job {job_id}: {str(e)}", exc_info=True)
            job.status = "failed"
            job.error_message = str(e)
            job.current_step = f"Failed: {str(e)}"
            db.commit()
            return job

    @classmethod
    def _deduplicate_findings(cls, findings: List[Finding]) -> List[Finding]:
        """
        Deduplicates overlapping findings by rule_id or identical title/observation.
        """
        seen_rules = set()
        deduped = []
        for f in findings:
            key = (f.rule_id, f.title)
            if key not in seen_rules:
                seen_rules.add(key)
                deduped.append(f)
        return deduped

    @classmethod
    def _persist_analysis_results(
        cls,
        db: Session,
        job: AnalysisJob,
        engine_runs_data: List[Dict[str, Any]],
        readiness_score_resp: Any,
        complete_report: Any,
        export_paths: Dict[str, str],
    ):
        for run_info in engine_runs_data:
            eng_type: EngineType = run_info["type"]
            eng_result: EngineResult = run_info["result"]

            run_row = AnalysisRun(
                job_id=job.id,
                engine_type=eng_type.value,
                status=eng_result.status,
                execution_time_ms=eng_result.execution_time_ms,
                config_snapshot=eng_result.summary,
            )
            db.add(run_row)
            db.flush()

            # Persist individual findings
            for f in eng_result.findings:
                v_row = VerificationResult(
                    analysis_run_id=run_row.id,
                    rule_id=f.rule_id,
                    category=f.category,
                    status=f.status.value,
                    severity=f.severity.value,
                    expected_requirement=f.expected_requirement,
                    actual_observation=f.actual_observation,
                    evidence=f.evidence,
                    source_location=f.source_location.model_dump() if f.source_location else None,
                    suggested_correction=f.suggested_correction,
                    confidence=f.confidence,
                    is_provisional=f.is_provisional,
                )
                db.add(v_row)

        # Persist ReadinessScore
        score_row = ReadinessScore(
            job_id=job.id,
            overall_score=readiness_score_resp.overall_score,
            is_provisional=readiness_score_resp.is_provisional,
            category_scores={k: v.model_dump() for k, v in readiness_score_resp.category_scores.items()},
            critical_issues_count=readiness_score_resp.critical_issues_count,
            warnings_count=readiness_score_resp.warnings_count,
            unverified_count=readiness_score_resp.unverified_count,
            calculation_breakdown=readiness_score_resp.breakdown.model_dump(),
        )
        db.add(score_row)

        # Persist GeneratedReport
        report_row = GeneratedReport(
            job_id=job.id,
            report_json=complete_report.model_dump(mode="json"),
            pdf_storage_path=export_paths.get("pdf_path"),
            docx_storage_path=export_paths.get("docx_path"),
        )
        db.add(report_row)

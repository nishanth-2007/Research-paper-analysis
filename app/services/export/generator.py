from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.schemas.common import Finding, CheckStatus, Severity
from app.schemas.scoring import ReadinessScoreResponse
from app.schemas.academic import AcademicCriterionAssessment
from app.schemas.report import (
    CompleteAnalysisReport,
    ExecutiveSummary,
    VerificationLimitation,
    ActionableRecommendation,
)
from app.services.scoring.engine import ReadinessScoringEngine
from app.services.export.pdf_exporter import PDFReportExporter
from app.services.export.docx_exporter import DOCXReportExporter
from app.services.storage import get_storage_service
from app.services.scoring.deduplicator import IssueDeduplicator


class ReportGenerator:
    @classmethod
    def build_report(
        cls,
        analysis_id: str,
        manuscript_id: str,
        version_id: str,
        manuscript_title: str,
        findings: List[Finding],
        readiness_score: ReadinessScoreResponse,
        journal_id: Optional[str] = None,
        journal_name: Optional[str] = None,
        guideline_version_tag: Optional[str] = None,
        academic_assessments: Optional[List[AcademicCriterionAssessment]] = None,
        document_validation: Optional[Dict[str, Any]] = None,
    ) -> CompleteAnalysisReport:
        critical_issues = [f for f in findings if f.status == CheckStatus.FAIL and f.severity == Severity.CRITICAL]
        warnings = [f for f in findings if f.status == CheckStatus.WARNING]
        unverified = [f for f in findings if f.status == CheckStatus.UNABLE_TO_VERIFY]

        # Consolidated deduplicated issues
        consolidated_issues = IssueDeduplicator.consolidate_findings(findings)
        coverage = IssueDeduplicator.calculate_coverage(findings)

        # Executive summary synthesis
        strengths = [f.title for f in findings if f.status == CheckStatus.PASS][:3]
        deficits = [f.title for f in findings if f.status == CheckStatus.FAIL][:3]

        blockers_count = sum(1 for c in consolidated_issues if c.tier.value == "submission_blocker")
        improvements_count = sum(1 for c in consolidated_issues if c.tier.value == "improvement_recommended")

        synthesis = (
            f"Manuscript evaluated against {journal_name or 'standard academic submission'} guidelines. "
            f"Overall Readiness Score: {readiness_score.overall_score:.1f}/100 ({readiness_score.readiness_tier}). "
            f"Verification coverage is {coverage.coverage_percent}% across {coverage.total_checks} checks. "
            f"Found {blockers_count} confirmed submission blocker(s) and {improvements_count} recommended improvement(s)."
        )

        exec_summary = ExecutiveSummary(
            manuscript_title=manuscript_title,
            target_journal=journal_name,
            overall_score=readiness_score.overall_score,
            readiness_tier=readiness_score.readiness_tier,
            key_strengths=strengths,
            critical_deficits=deficits,
            synthesis=synthesis,
        )

        recommendations = ReadinessScoringEngine.rank_actionable_recommendations(findings)

        limitations = [
            VerificationLimitation(
                engine="Deterministic Verification Engine",
                scope="Layout & Margins",
                reason="Inspection is performed on rendered PDF coordinate blocks and font descriptors.",
                guidance="Ensure final LaTeX/Word source files match the official camera-ready template.",
            ),
            VerificationLimitation(
                engine="LLM Academic Evaluation Engine",
                scope="Novelty & Originality",
                reason="AI novelty heuristics evaluate stated differentiators but cannot guarantee absolute prior art novelty.",
                guidance="Conduct formal bibliographic searches across IEEE Xplore, ACM Digital Library, and Google Scholar.",
            ),
        ]

        return CompleteAnalysisReport(
            analysis_id=analysis_id,
            manuscript_id=manuscript_id,
            version_id=version_id,
            manuscript_title=manuscript_title,
            target_journal_id=journal_id,
            target_journal_name=journal_name,
            guideline_version_tag=guideline_version_tag,
            generated_at=datetime.now(timezone.utc),
            document_validation=document_validation,
            verification_coverage=coverage,
            consolidated_issues=consolidated_issues,
            executive_summary=exec_summary,
            readiness_score=readiness_score,
            all_findings=findings,
            critical_issues=critical_issues,
            warnings=warnings,
            unverified_checks=unverified,
            actionable_recommendations=recommendations,
            academic_assessments=academic_assessments or [],
            limitations=limitations,
        )

    @classmethod
    def export_and_store_report_files(
        cls,
        report: CompleteAnalysisReport,
    ) -> Dict[str, str]:
        """
        Generates PDF and DOCX files, saves them in object storage, and returns their paths.
        """
        storage = get_storage_service()

        # PDF export
        pdf_bytes = PDFReportExporter.generate_pdf_bytes(report)
        pdf_path = storage.save_file(
            content=pdf_bytes,
            filename=f"readiness_report_{report.analysis_id}.pdf",
            subfolder="reports",
        )

        # DOCX export
        docx_bytes = DOCXReportExporter.generate_docx_bytes(report)
        docx_path = storage.save_file(
            content=docx_bytes,
            filename=f"readiness_report_{report.analysis_id}.docx",
            subfolder="reports",
        )

        return {"pdf_path": pdf_path, "docx_path": docx_path}

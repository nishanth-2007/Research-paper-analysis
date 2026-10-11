import time
from typing import Optional, Dict, Any, List
from pydantic import ValidationError

from app.schemas.common import (
    EngineResult,
    EngineType,
    Finding,
    CheckStatus,
    Severity,
    SourceLocation,
)
from app.schemas.academic import LLMAcademicEvaluationOutput, AcademicCriterionAssessment
from app.services.engines.base import BaseEvaluationEngine
from app.services.ingestion.extractor import ExtractedDocument
from app.models.journal import GuidelineVersion
from app.services.engines.academic.llm_provider import get_llm_provider
from app.services.engines.academic.prompts import (
    SYSTEM_ACADEMIC_EVALUATOR_PROMPT,
    build_academic_evaluation_prompt,
)


class AcademicLLMEngine(BaseEvaluationEngine):
    def evaluate(
        self,
        document: ExtractedDocument,
        guideline_version: Optional[GuidelineVersion] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> EngineResult:
        start_time = time.perf_counter()
        findings: List[Finding] = []

        # Scanned PDF check
        if document.is_scanned or document.ocr_required:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            findings.append(Finding(
                rule_id="LLM_ACADEMIC_SCANNED_UNABLE_TO_VERIFY",
                engine=EngineType.LLM_ACADEMIC,
                category="methodology_rigor",
                status=CheckStatus.UNABLE_TO_VERIFY,
                severity=Severity.CRITICAL,
                title="Academic Quality Evaluation Impaired on Scanned Document",
                expected_requirement="Extractable text representations are required for semantic analysis.",
                actual_observation="Scanned PDF requires OCR before semantic academic quality checks can proceed.",
                is_provisional=True,
                suggested_correction="Perform OCR or submit digital source manuscript.",
                confidence=1.0,
            ))
            return EngineResult(
                engine=EngineType.LLM_ACADEMIC,
                execution_time_ms=round(elapsed_ms, 2),
                status="completed",
                findings=findings,
                summary={"provisional": True},
            )

        journal_name = guideline_version.journal.name if (guideline_version and guideline_version.journal) else "General Peer-Reviewed Venue"

        # Locate abstract
        abstract_text = ""
        for s in document.sections:
            if s.get("normalized_title") == "abstract":
                abstract_text = s.get("content", "")
                break
        if not abstract_text and document.sections:
            abstract_text = document.sections[0].get("content", "")[:1000]

        prompt = build_academic_evaluation_prompt(
            title=document.title,
            abstract=abstract_text,
            sections=document.sections,
            target_journal_name=journal_name,
        )

        provider = get_llm_provider()

        try:
            raw_json = provider.generate_json(
                prompt=prompt,
                system_prompt=SYSTEM_ACADEMIC_EVALUATOR_PROMPT,
            )

            # Strict Pydantic Validation
            validated_output = LLMAcademicEvaluationOutput.model_validate(raw_json)

            # Convert to normalized Finding objects
            for item in validated_output.assessments:
                status, severity = self._map_grade_to_status(item.assessment)
                category = self._map_criterion_to_category(item.criterion)

                loc = None
                evidence_text = None
                if item.supporting_excerpts:
                    first_exc = item.supporting_excerpts[0]
                    loc = SourceLocation(
                        section_name=first_exc.section,
                        page_number=first_exc.page,
                        snippet=first_exc.excerpt,
                    )
                    evidence_text = first_exc.excerpt

                findings.append(Finding(
                    rule_id=f"LLM_ACADEMIC_{item.criterion.upper()}",
                    engine=EngineType.LLM_ACADEMIC,
                    category=category,
                    status=status,
                    severity=severity,
                    title=f"Academic Evaluation: {item.criterion.replace('_', ' ').title()}",
                    expected_requirement=f"Rigorous academic execution conforming to peer review standards for {journal_name}.",
                    actual_observation=item.explanation,
                    evidence=evidence_text,
                    source_location=loc,
                    suggested_correction=item.recommended_action,
                    confidence=item.confidence,
                    is_provisional=(item.criterion == "technical_contribution_and_novelty"),
                    metadata={
                        "assessment_grade": item.assessment,
                        "limitations": item.limitations,
                        "relevant_sources": item.relevant_sources,
                    },
                ))

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return EngineResult(
                engine=EngineType.LLM_ACADEMIC,
                execution_time_ms=round(elapsed_ms, 2),
                status="completed",
                findings=findings,
                summary={
                    "assessments_count": len(validated_output.assessments),
                    "strengths": validated_output.overall_strengths,
                    "critical_deficiencies": validated_output.critical_deficiencies,
                    "preliminary_notice": validated_output.preliminary_notice,
                },
            )

        except (ValidationError, Exception) as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            # Resilient fallback: return partial failure without breaking the entire pipeline
            fallback_finding = Finding(
                rule_id="LLM_ACADEMIC_EVAL_DEGRADED",
                engine=EngineType.LLM_ACADEMIC,
                category="methodology_rigor",
                status=CheckStatus.WARNING,
                severity=Severity.MODERATE,
                title="Academic Qualitative Evaluation Degraded",
                expected_requirement="AI qualitative assessment response format parsing.",
                actual_observation=f"Evaluation service encountered an intermittent formatting or communication anomaly: {str(e)}",
                suggested_correction="Retry analysis run.",
                confidence=0.5,
                is_provisional=True,
            )
            return EngineResult(
                engine=EngineType.LLM_ACADEMIC,
                execution_time_ms=round(elapsed_ms, 2),
                status="partial_failure",
                findings=[fallback_finding],
                summary={"degraded": True},
                error_message=str(e),
            )

    @staticmethod
    def _map_grade_to_status(assessment: str) -> tuple[CheckStatus, Severity]:
        grade = assessment.lower()
        if grade == "strong":
            return CheckStatus.PASS, Severity.INFO
        elif grade == "adequate":
            return CheckStatus.PASS, Severity.INFO
        elif grade == "weak":
            return CheckStatus.WARNING, Severity.MODERATE
        else:  # needs_revision
            return CheckStatus.FAIL, Severity.MAJOR

    @staticmethod
    def _map_criterion_to_category(criterion: str) -> str:
        c = criterion.lower()
        if "novelty" in c or "contribution" in c:
            return "methodology_rigor"
        elif "method" in c or "claim" in c or "evidence" in c:
            return "methodology_rigor"
        elif "question" in c or "scope" in c:
            return "scope_alignment"
        return "methodology_rigor"

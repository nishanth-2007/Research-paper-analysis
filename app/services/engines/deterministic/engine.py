import time
from typing import Optional, Dict, Any, List
from app.schemas.common import EngineResult, EngineType, Finding
from app.services.engines.base import BaseEvaluationEngine
from app.services.ingestion.extractor import ExtractedDocument
from app.models.journal import GuidelineVersion
from app.services.engines.deterministic.citation_checker import CitationChecker
from app.services.engines.deterministic.section_checker import SectionChecker
from app.services.engines.deterministic.figure_table_checker import FigureTableChecker
from app.services.engines.deterministic.layout_checker import LayoutChecker


class DeterministicEngine(BaseEvaluationEngine):
    def evaluate(
        self,
        document: ExtractedDocument,
        guideline_version: Optional[GuidelineVersion] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> EngineResult:
        start_time = time.perf_counter()
        findings: List[Finding] = []

        # Extract journal-specific rule parameters if available
        rule_params: Dict[str, Any] = {}
        if guideline_version and guideline_version.rules:
            for rule in guideline_version.rules:
                if rule.rule_parameters:
                    rule_params.update(rule.rule_parameters)

        if config:
            rule_params.update(config)

        try:
            # 1. Section presence and word counts
            sec_findings = SectionChecker.verify(document, rule_params=rule_params)
            findings.extend(sec_findings)

            # 2. Citation and Reference integrity
            cit_findings = CitationChecker.verify(document)
            findings.extend(cit_findings)

            # 3. Figure and Table numbering & mentions
            fig_findings = FigureTableChecker.verify(document)
            findings.extend(fig_findings)

            # 4. Layout, pages, typography
            layout_findings = LayoutChecker.verify(document, rule_params=rule_params)
            findings.extend(layout_findings)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            summary = {
                "total_checks": len(findings),
                "passed_checks": sum(1 for f in findings if f.status.value == "pass"),
                "failed_checks": sum(1 for f in findings if f.status.value == "fail"),
                "warnings": sum(1 for f in findings if f.status.value == "warning"),
                "unverified": sum(1 for f in findings if f.status.value == "unable_to_verify"),
            }

            return EngineResult(
                engine=EngineType.DETERMINISTIC,
                execution_time_ms=round(elapsed_ms, 2),
                status="completed",
                findings=findings,
                summary=summary,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return EngineResult(
                engine=EngineType.DETERMINISTIC,
                execution_time_ms=round(elapsed_ms, 2),
                status="failed",
                findings=findings,
                summary={},
                error_message=f"Deterministic engine execution error: {str(e)}",
            )

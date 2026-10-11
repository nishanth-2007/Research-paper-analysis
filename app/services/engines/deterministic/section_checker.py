from typing import List, Dict, Any, Optional
from app.schemas.common import Finding, CheckStatus, Severity, EngineType, SourceLocation
from app.services.ingestion.extractor import ExtractedDocument


REQUIRED_CORE_SECTIONS = [
    {"canonical": "abstract", "label": "Abstract", "severity": Severity.CRITICAL},
    {"canonical": "introduction", "label": "Introduction", "severity": Severity.CRITICAL},
    {"canonical": "methodology", "label": "Methodology / Methods", "severity": Severity.CRITICAL},
    {"canonical": "results", "label": "Results / Evaluation", "severity": Severity.MAJOR},
    {"canonical": "conclusion", "label": "Conclusion", "severity": Severity.MAJOR},
]


class SectionChecker:
    @staticmethod
    def verify(
        document: ExtractedDocument,
        rule_params: Optional[Dict[str, Any]] = None,
    ) -> List[Finding]:
        findings: List[Finding] = []

        if document.is_scanned or document.ocr_required:
            findings.append(Finding(
                rule_id="DETERM_SEC_UNABLE_TO_INSPECT",
                engine=EngineType.DETERMINISTIC,
                category="manuscript_completeness",
                status=CheckStatus.UNABLE_TO_VERIFY,
                severity=Severity.CRITICAL,
                title="Section Structure Cannot Be Inspected on Scanned Document",
                expected_requirement="Document must have extractable headings to verify manuscript completeness.",
                actual_observation="Scanned document lacks machine-readable headings.",
                is_provisional=True,
                suggested_correction="Submit an unrasterized PDF or perform OCR text extraction.",
                confidence=1.0,
            ))
            return findings

        if hasattr(document, "validation") and document.validation and not document.validation.is_plausible_manuscript:
            findings.append(Finding(
                rule_id="DETERM_DOC_NON_MANUSCRIPT_PLAUSIBILITY",
                engine=EngineType.DETERMINISTIC,
                category="manuscript_completeness",
                status=CheckStatus.UNABLE_TO_VERIFY,
                severity=Severity.MAJOR,
                title="Section Verification Suspended (Non-Journal Manuscript Detected)",
                expected_requirement="Document must be a research manuscript formatted with standard sections for journal submission.",
                actual_observation=document.validation.warning_message or "Uploaded file does not match journal research manuscript structure.",
                is_provisional=True,
                suggested_correction="Upload a research manuscript (.pdf or .docx) formatted with standard sections required for journal submission.",
                confidence=document.validation.confidence,
                metadata={"document_type": document.validation.document_type},
            ))
            return findings

        detected_canonicals = {s["normalized_title"]: s for s in document.sections}

        # 1. Check for missing essential sections
        for req in REQUIRED_CORE_SECTIONS:
            canon = req["canonical"]
            if canon not in detected_canonicals:
                findings.append(Finding(
                    rule_id=f"DETERM_SEC_MISSING_{canon.upper()}",
                    engine=EngineType.DETERMINISTIC,
                    category="manuscript_completeness",
                    status=CheckStatus.FAIL,
                    severity=req["severity"],
                    title=f"Missing Required Section: {req['label']}",
                    expected_requirement=f"Target journal submission guidelines require an explicit '{req['label']}' section.",
                    actual_observation=f"No section matching '{req['label']}' was identified in the document structure.",
                    suggested_correction=f"Add a clearly demarcated '{req['label']}' section heading with content.",
                    confidence=0.95,
                ))
            else:
                s_data = detected_canonicals[canon]
                w_count = s_data.get("word_count", 0)
                if w_count < 30 and canon != "abstract":
                    findings.append(Finding(
                        rule_id=f"DETERM_SEC_TOO_SHORT_{canon.upper()}",
                        engine=EngineType.DETERMINISTIC,
                        category="manuscript_completeness",
                        status=CheckStatus.WARNING,
                        severity=Severity.MODERATE,
                        title=f"Truncated / Incomplete Section: {req['label']}",
                        expected_requirement=f"{req['label']} section should contain comprehensive discourse.",
                        actual_observation=f"{req['label']} section contains only {w_count} words.",
                        evidence=s_data.get("content", "")[:150],
                        source_location=SourceLocation(page_number=s_data.get("start_page"), section_name=s_data.get("title")),
                        suggested_correction=f"Expand the {req['label']} section to adequately detail the research.",
                        confidence=0.9,
                    ))

        # 2. Abstract word count checks
        params = rule_params or {}
        min_abstract_words = params.get("min_abstract_words", 100)
        max_abstract_words = params.get("max_abstract_words", 250)

        if "abstract" in detected_canonicals:
            abs_sec = detected_canonicals["abstract"]
            abs_words = abs_sec.get("word_count", 0)

            if abs_words < min_abstract_words:
                findings.append(Finding(
                    rule_id="DETERM_ABS_WORD_COUNT_LOW",
                    engine=EngineType.DETERMINISTIC,
                    category="compliance_formatting",
                    status=CheckStatus.WARNING,
                    severity=Severity.MODERATE,
                    title="Abstract Word Count Below Minimum Guideline",
                    expected_requirement=f"Abstract should typically contain at least {min_abstract_words} words.",
                    actual_observation=f"Detected abstract contains {abs_words} words.",
                    evidence=abs_sec.get("content", "")[:200],
                    source_location=SourceLocation(page_number=abs_sec.get("start_page"), section_name="Abstract"),
                    suggested_correction=f"Expand abstract to thoroughly summarize objective, methodology, results, and significance (at least {min_abstract_words} words).",
                    confidence=1.0,
                ))
            elif abs_words > max_abstract_words:
                findings.append(Finding(
                    rule_id="DETERM_ABS_WORD_COUNT_HIGH",
                    engine=EngineType.DETERMINISTIC,
                    category="compliance_formatting",
                    status=CheckStatus.FAIL,
                    severity=Severity.MAJOR,
                    title="Abstract Exceeds Maximum Word Limit",
                    expected_requirement=f"Abstract must not exceed {max_abstract_words} words per journal guidelines.",
                    actual_observation=f"Detected abstract contains {abs_words} words ({abs_words - max_abstract_words} words over limit).",
                    evidence=abs_sec.get("content", "")[:200],
                    source_location=SourceLocation(page_number=abs_sec.get("start_page"), section_name="Abstract"),
                    suggested_correction=f"Condense the abstract to within the {max_abstract_words}-word limit.",
                    confidence=1.0,
                ))
            else:
                findings.append(Finding(
                    rule_id="DETERM_ABS_WORD_COUNT_PASS",
                    engine=EngineType.DETERMINISTIC,
                    category="compliance_formatting",
                    status=CheckStatus.PASS,
                    severity=Severity.INFO,
                    title="Abstract Length Complies with Guidelines",
                    expected_requirement=f"Abstract length within {min_abstract_words} - {max_abstract_words} words.",
                    actual_observation=f"Abstract length is {abs_words} words.",
                    source_location=SourceLocation(page_number=abs_sec.get("start_page"), section_name="Abstract"),
                    confidence=1.0,
                ))

        return findings

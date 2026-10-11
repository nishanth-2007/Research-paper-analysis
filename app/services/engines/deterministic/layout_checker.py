from typing import List, Dict, Any, Optional
from app.schemas.common import Finding, CheckStatus, Severity, EngineType, SourceLocation
from app.services.ingestion.extractor import ExtractedDocument


class LayoutChecker:
    @staticmethod
    def verify(
        document: ExtractedDocument,
        rule_params: Optional[Dict[str, Any]] = None,
    ) -> List[Finding]:
        findings: List[Finding] = []

        params = rule_params or {}
        min_pages = params.get("min_pages", 4)
        max_pages = params.get("max_pages", 15)

        # 1. Scanned Document inspection limitation
        if document.is_scanned or document.ocr_required:
            findings.append(Finding(
                rule_id="DETERM_LAYOUT_SCANNED_UNABLE_TO_VERIFY",
                engine=EngineType.DETERMINISTIC,
                category="compliance_formatting",
                status=CheckStatus.UNABLE_TO_VERIFY,
                severity=Severity.MAJOR,
                title="Formatting & Typography Verification Incomplete (Scanned Artifact)",
                expected_requirement="Electronic manuscript files must contain vector glyphs and style attributes to inspect fonts and margins.",
                actual_observation=document.layout_metrics.get("ocr_diagnostic", "Raster scanned pages detected; font sizes and layout cannot be verified directly."),
                is_provisional=True,
                suggested_correction="Compile original LaTeX or DOCX manuscript to PDF to allow full font and margin compliance verification.",
                confidence=1.0,
            ))
            return findings

        # 2. Page count limit check
        pages = document.page_count
        if pages < min_pages:
            findings.append(Finding(
                rule_id="DETERM_PAGE_COUNT_LOW",
                engine=EngineType.DETERMINISTIC,
                category="compliance_formatting",
                status=CheckStatus.WARNING,
                severity=Severity.MODERATE,
                title="Manuscript Page Count Below Expected Minimum",
                expected_requirement=f"Standard full research papers typically require at least {min_pages} pages.",
                actual_observation=f"Manuscript has {pages} page(s).",
                suggested_correction=f"Expand literature review, experimental details, or discussion to meet full paper depth standards (at least {min_pages} pages).",
                confidence=1.0,
            ))
        elif pages > max_pages:
            findings.append(Finding(
                rule_id="DETERM_PAGE_COUNT_HIGH",
                engine=EngineType.DETERMINISTIC,
                category="compliance_formatting",
                status=CheckStatus.FAIL,
                severity=Severity.CRITICAL,
                title="Manuscript Page Count Exceeds Journal Limit",
                expected_requirement=f"Maximum allowed page length is {max_pages} pages.",
                actual_observation=f"Manuscript has {pages} pages ({pages - max_pages} page(s) over limit).",
                suggested_correction=f"Trim narrative or move secondary tables/derivations into an Appendix/Supplementary Material to fit within {max_pages} pages.",
                confidence=1.0,
            ))
        else:
            findings.append(Finding(
                rule_id="DETERM_PAGE_COUNT_PASS",
                engine=EngineType.DETERMINISTIC,
                category="compliance_formatting",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                title="Page Count Complies with Submission Limits",
                expected_requirement=f"Page count must be within {min_pages} to {max_pages} pages.",
                actual_observation=f"Manuscript page count is {pages} page(s).",
                confidence=1.0,
            ))

        # 3. Typography & Font Size verification from PyMuPDF
        avg_font = document.layout_metrics.get("avg_font_size_pt")
        if avg_font:
            if avg_font < 8.5:
                findings.append(Finding(
                    rule_id="DETERM_FONT_SIZE_TOO_SMALL",
                    engine=EngineType.DETERMINISTIC,
                    category="compliance_formatting",
                    status=CheckStatus.FAIL,
                    severity=Severity.MAJOR,
                    title="Average Font Size Unusually Small",
                    expected_requirement="Journal manuscripts require standard readable body typography (9.5pt - 12pt).",
                    actual_observation=f"Detected average font size is {avg_font}pt, which may violate journal readability and page-packing rules.",
                    suggested_correction="Adjust body text font size to the journal template standard (e.g., 10pt IEEE or 11pt/12pt standard).",
                    confidence=0.85,
                ))
            elif avg_font > 14.0:
                findings.append(Finding(
                    rule_id="DETERM_FONT_SIZE_TOO_LARGE",
                    engine=EngineType.DETERMINISTIC,
                    category="compliance_formatting",
                    status=CheckStatus.WARNING,
                    severity=Severity.MODERATE,
                    title="Average Body Font Size Appears Abnormally Large",
                    expected_requirement="Body typography should adhere to journal template sizing (10pt - 12pt).",
                    actual_observation=f"Detected average font size is {avg_font}pt.",
                    suggested_correction="Ensure body paragraphs use standard template font sizing.",
                    confidence=0.85,
                ))
            else:
                findings.append(Finding(
                    rule_id="DETERM_TYPOGRAPHY_PASS",
                    engine=EngineType.DETERMINISTIC,
                    category="compliance_formatting",
                    status=CheckStatus.PASS,
                    severity=Severity.INFO,
                    title="Typography and Body Font Size Verified",
                    expected_requirement="Body text size should conform to journal template standards (~10-12pt).",
                    actual_observation=f"Average detected font size is {avg_font}pt.",
                    confidence=0.9,
                ))

        return findings

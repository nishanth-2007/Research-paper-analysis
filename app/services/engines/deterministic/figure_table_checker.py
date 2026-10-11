import re
from typing import List, Dict, Any, Set
from app.schemas.common import Finding, CheckStatus, Severity, EngineType, SourceLocation
from app.services.ingestion.extractor import ExtractedDocument


class FigureTableChecker:
    @staticmethod
    def verify(document: ExtractedDocument) -> List[Finding]:
        findings: List[Finding] = []

        if document.is_scanned or document.ocr_required:
            return findings  # Handled by global scan check

        figures = document.figures
        tables = document.tables
        full_text = document.raw_text

        # 1. Figure verification
        fig_nums_found: List[int] = []
        for fig in figures:
            raw_num = fig.get("figure_num", "")
            if raw_num.isdigit():
                fig_num = int(raw_num)
                fig_nums_found.append(fig_num)

                # Check if referenced in body text
                # e.g., "Figure 1", "Fig. 1", "Figure 1:", "Fig 1"
                ref_pattern = re.compile(rf"\b(fig(?:ure|\.)?\s*{fig_num})\b", re.IGNORECASE)
                matches = list(ref_pattern.finditer(full_text))

                # Note: at least 1 match is the caption itself. If only 1 match or matches all in caption text, uncited in body!
                # Let's count matches that don't match the caption text snippet
                body_mentions = 0
                caption_text = fig.get("caption", "").strip()
                text_without_caption = full_text.replace(caption_text, "")
                body_mentions = len(ref_pattern.findall(text_without_caption))

                if body_mentions == 0:
                    findings.append(Finding(
                        rule_id=f"DETERM_FIG_UNREFERENCED_{fig_num}",
                        engine=EngineType.DETERMINISTIC,
                        category="compliance_formatting",
                        status=CheckStatus.WARNING,
                        severity=Severity.MODERATE,
                        title=f"Figure {fig_num} Is Not Referenced in Text",
                        expected_requirement=f"All figures (Figure {fig_num}) must be referenced and discussed in the narrative text.",
                        actual_observation=f"Figure {fig_num} has a caption on page {fig.get('page')}, but no citation (e.g. 'see Fig. {fig_num}') was found in the body paragraphs.",
                        evidence=fig.get("caption"),
                        source_location=SourceLocation(page_number=fig.get("page")),
                        suggested_correction=f"Add an in-text reference explaining Figure {fig_num} in the methodology or results section.",
                        confidence=0.9,
                    ))

        # Check Figure numbering gaps
        if fig_nums_found:
            sorted_figs = sorted(set(fig_nums_found))
            expected = list(range(1, max(sorted_figs) + 1))
            missing_in_seq = [x for x in expected if x not in sorted_figs]
            if missing_in_seq:
                findings.append(Finding(
                    rule_id="DETERM_FIG_NUMBERING_GAP",
                    engine=EngineType.DETERMINISTIC,
                    category="compliance_formatting",
                    status=CheckStatus.FAIL,
                    severity=Severity.MINOR,
                    title="Figure Numbering Discontinuity",
                    expected_requirement="Figures must be numbered sequentially without missing indices.",
                    actual_observation=f"Detected figures {sorted_figs}, but Figure(s) {missing_in_seq} appear to be missing.",
                    suggested_correction="Renumber figures consecutively in order of their appearance in the manuscript.",
                    confidence=0.95,
                ))

        # 2. Table verification
        tbl_nums_found: List[int] = []
        for tbl in tables:
            raw_num = tbl.get("table_num", "")
            if raw_num.isdigit():
                tbl_num = int(raw_num)
                tbl_nums_found.append(tbl_num)

                # Check if referenced in body text
                ref_pattern = re.compile(rf"\b(table\s*{tbl_num})\b", re.IGNORECASE)
                caption_text = tbl.get("caption", "").strip()
                text_without_caption = full_text.replace(caption_text, "")
                body_mentions = len(ref_pattern.findall(text_without_caption))

                if body_mentions == 0:
                    findings.append(Finding(
                        rule_id=f"DETERM_TBL_UNREFERENCED_{tbl_num}",
                        engine=EngineType.DETERMINISTIC,
                        category="compliance_formatting",
                        status=CheckStatus.WARNING,
                        severity=Severity.MODERATE,
                        title=f"Table {tbl_num} Is Not Referenced in Text",
                        expected_requirement=f"All tables (Table {tbl_num}) must be explicitly referenced and discussed in the narrative text.",
                        actual_observation=f"Table {tbl_num} is defined on page {tbl.get('page')}, but no corresponding in-text reference ('as shown in Table {tbl_num}') was identified.",
                        evidence=tbl.get("caption"),
                        source_location=SourceLocation(page_number=tbl.get("page")),
                        suggested_correction=f"Reference and discuss Table {tbl_num} in the results or evaluation section.",
                        confidence=0.9,
                    ))

        # Check Table numbering gaps
        if tbl_nums_found:
            sorted_tbls = sorted(set(tbl_nums_found))
            expected_tbls = list(range(1, max(sorted_tbls) + 1))
            missing_tbl_seq = [x for x in expected_tbls if x not in sorted_tbls]
            if missing_tbl_seq:
                findings.append(Finding(
                    rule_id="DETERM_TBL_NUMBERING_GAP",
                    engine=EngineType.DETERMINISTIC,
                    category="compliance_formatting",
                    status=CheckStatus.FAIL,
                    severity=Severity.MINOR,
                    title="Table Numbering Discontinuity",
                    expected_requirement="Tables must be numbered consecutively starting from 1.",
                    actual_observation=f"Detected tables {sorted_tbls}, with missing index(es) {missing_tbl_seq}.",
                    suggested_correction="Ensure tables are sequentially numbered in chronological appearance.",
                    confidence=0.95,
                ))

        if figures and tables and not findings:
            findings.append(Finding(
                rule_id="DETERM_FIG_TBL_OK",
                engine=EngineType.DETERMINISTIC,
                category="compliance_formatting",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                title="Figure and Table Numbering & Citations Verified",
                expected_requirement="All figures and tables must be numbered sequentially and referenced in text.",
                actual_observation=f"Verified {len(figures)} figure(s) and {len(tables)} table(s) with sequential numbering and body citations.",
                confidence=1.0,
            ))

        return findings

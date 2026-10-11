from app.services.ingestion.extractor import DocumentExtractor
from app.services.engines.deterministic import (
    DeterministicEngine,
    CitationChecker,
    SectionChecker,
    FigureTableChecker,
    LayoutChecker,
)
from app.schemas.common import CheckStatus, Severity


def test_deterministic_citation_checker_pass(valid_pdf_bytes):
    doc = DocumentExtractor.extract_document(valid_pdf_bytes, "valid.pdf")
    findings = CitationChecker.verify(doc)

    # Should have a PASS finding for citation consistency
    pass_findings = [f for f in findings if f.status == CheckStatus.PASS]
    fail_findings = [f for f in findings if f.status == CheckStatus.FAIL]
    assert len(pass_findings) >= 1
    assert len(fail_findings) == 0


def test_deterministic_flawed_citations(flawed_pdf_bytes):
    doc = DocumentExtractor.extract_document(flawed_pdf_bytes, "flawed.pdf")
    findings = CitationChecker.verify(doc)

    # Must detect missing reference for citation [99]
    missing_99 = [f for f in findings if "99" in f.rule_id and f.status == CheckStatus.FAIL]
    assert len(missing_99) == 1
    assert missing_99[0].severity == Severity.CRITICAL

    # Must detect uncited reference [3]
    uncited_3 = [f for f in findings if "UNCITED_3" in f.rule_id and f.status == CheckStatus.WARNING]
    assert len(uncited_3) == 1


def test_deterministic_section_checker_flawed(flawed_pdf_bytes):
    doc = DocumentExtractor.extract_document(flawed_pdf_bytes, "flawed.pdf")
    findings = SectionChecker.verify(doc)

    # Must detect missing Conclusion
    missing_concl = [f for f in findings if "MISSING_CONCLUSION" in f.rule_id]
    assert len(missing_concl) == 1
    assert missing_concl[0].status == CheckStatus.FAIL

    # Must detect short abstract
    short_abs = [f for f in findings if "ABS_WORD_COUNT_LOW" in f.rule_id]
    assert len(short_abs) == 1


def test_deterministic_unreferenced_figure(flawed_pdf_bytes):
    doc = DocumentExtractor.extract_document(flawed_pdf_bytes, "flawed.pdf")
    findings = FigureTableChecker.verify(doc)

    # Figure 2 is in the document but not referenced in body text
    unref_fig = [f for f in findings if "FIG_UNREFERENCED_2" in f.rule_id]
    assert len(unref_fig) == 1
    assert unref_fig[0].status == CheckStatus.WARNING


def test_deterministic_scanned_pdf_unverifiable(scanned_pdf_bytes):
    doc = DocumentExtractor.extract_document(scanned_pdf_bytes, "scanned.pdf")
    findings = LayoutChecker.verify(doc)

    # Layout checker must report UNABLE_TO_VERIFY and provisional
    unverified = [f for f in findings if f.status == CheckStatus.UNABLE_TO_VERIFY]
    assert len(unverified) >= 1
    assert unverified[0].is_provisional is True


def test_deterministic_engine_full_run(valid_pdf_bytes):
    doc = DocumentExtractor.extract_document(valid_pdf_bytes, "valid.pdf")
    engine = DeterministicEngine()
    result = engine.evaluate(document=doc)

    assert result.status == "completed"
    assert result.execution_time_ms > 0
    assert len(result.findings) >= 3
    assert "total_checks" in result.summary

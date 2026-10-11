import pytest
from app.services.ingestion.extractor import DocumentExtractor
from app.services.ingestion.normalizer import calculate_file_hash, normalize_section_title
from app.services.ingestion.ocr_detector import OCRDetector


def test_pdf_extraction_success(valid_pdf_bytes):
    doc = DocumentExtractor.extract_document(valid_pdf_bytes, "paper.pdf")
    assert doc.page_count >= 2
    assert doc.word_count > 50
    assert not doc.is_scanned
    assert not doc.ocr_required
    assert len(doc.sections) >= 3

    # Check detected citations
    cit_keys = [c["key"] for c in doc.citations]
    assert "[1]" in cit_keys
    assert "[2]" in cit_keys

    # Check detected references
    assert len(doc.references) >= 2
    ref_indices = [r["index"] for r in doc.references]
    assert 1 in ref_indices
    assert 2 in ref_indices

    # Check figure captions
    assert len(doc.figures) >= 1
    assert doc.figures[0]["figure_num"] == "1"


def test_docx_extraction_success(valid_docx_bytes):
    doc = DocumentExtractor.extract_document(valid_docx_bytes, "manuscript.docx")
    assert doc.word_count > 40
    assert not doc.is_scanned
    assert len(doc.sections) >= 4
    assert len(doc.references) >= 2


def test_scanned_pdf_detection(scanned_pdf_bytes):
    is_scanned, ocr_required, reason = OCRDetector.inspect_pdf_scanned_state(scanned_pdf_bytes)
    assert is_scanned is True
    assert ocr_required is True

    doc = DocumentExtractor.extract_document(scanned_pdf_bytes, "scanned_doc.pdf")
    assert doc.is_scanned is True
    assert doc.ocr_required is True


def test_sha256_hash_consistency(valid_pdf_bytes):
    h1 = calculate_file_hash(valid_pdf_bytes)
    h2 = calculate_file_hash(valid_pdf_bytes)
    assert h1 == h2
    assert len(h1) == 64


def test_unsupported_format_rejection():
    with pytest.raises(ValueError, match="Unsupported document format"):
        DocumentExtractor.extract_document(b"random bytes", "test.xyz")


def test_section_title_normalization():
    assert normalize_section_title("1. INTRODUCTION") == "introduction"
    assert normalize_section_title("II. Related Work") == "literature_review"
    assert normalize_section_title("PROPOSED METHODOLOGY") == "methodology"
    assert normalize_section_title("Experimental Evaluation") == "results"
    assert normalize_section_title("5. CONCLUSION AND FUTURE WORK") == "conclusion"
    assert normalize_section_title("REFERENCES") == "references"

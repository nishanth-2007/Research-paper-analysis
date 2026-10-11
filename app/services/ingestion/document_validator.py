import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentValidationResult(BaseModel):
    is_plausible_manuscript: bool = True
    document_type: str = "research_manuscript"  # research_manuscript, resume_or_cv, brief_document, unreadable_or_corrupted
    confidence: float = 1.0
    detected_indicators: List[str] = Field(default_factory=list)
    warning_message: Optional[str] = None
    extraction_quality: str = "high"  # high, moderate, low, unusable


class DocumentPlausibilityValidator:
    """
    Validates whether an uploaded file is plausibly an academic research manuscript
    or a non-academic document (e.g., Curriculum Vitae, resume, cover letter, empty file).
    """

    CV_STRONG_PATTERNS = [
        (re.compile(r"\b(curriculum\s+vitae|resume)\b", re.IGNORECASE), "Explicit Résumé / CV title"),
        (re.compile(r"\b(education|academic background)\b", re.IGNORECASE), "Education section heading"),
        (re.compile(r"\b(technical\s+skills|core\s+competencies|skill\s+set)\b", re.IGNORECASE), "Technical skills block"),
        (re.compile(r"\b(work\s+experience|professional\s+experience|employment\s+history)\b", re.IGNORECASE), "Work experience block"),
        (re.compile(r"\b(b\.?tech|b\.?e\.?|bachelor of|m\.?tech|master of|cgpa|gpa\s*[:\=])\b", re.IGNORECASE), "Degree / GPA entry"),
        (re.compile(r"\b(linkedin\.com\/in|github\.com\/[a-zA-Z0-9_\-]+)\b", re.IGNORECASE), "Personal portfolio / LinkedIn link"),
        (re.compile(r"\b(mobile|phone)\s*:\s*\+?\d{1,4}", re.IGNORECASE), "Contact phone number header"),
    ]

    ACADEMIC_STRONG_PATTERNS = [
        (re.compile(r"^\s*(?:(?:\d+|[IVXLCDM]+)[\.\:\-\s]+)?abstract\b", re.IGNORECASE | re.MULTILINE), "Explicit Abstract section"),
        (re.compile(r"^\s*(?:(?:\d+|[IVXLCDM]+)[\.\:\-\s]+)?(?:references|bibliography)\b", re.IGNORECASE | re.MULTILINE), "Explicit References section"),
        (re.compile(r"^\s*(?:(?:\d+|[IVXLCDM]+)[\.\:\-\s]+)?(?:methodology|methods|system architecture)\b", re.IGNORECASE | re.MULTILINE), "Methodology section"),
        (re.compile(r"^\s*(?:(?:\d+|[IVXLCDM]+)[\.\:\-\s]+)?(?:experimental results|results and discussion)\b", re.IGNORECASE | re.MULTILINE), "Experimental Results section"),
        (re.compile(r"\b(ieee|acm|elsevier|springer|nature|arxiv)\b", re.IGNORECASE), "Publisher/Archive header metadata"),
    ]

    @classmethod
    def validate(
        cls,
        raw_text: str,
        page_count: int,
        word_count: int,
        is_scanned: bool,
        sections: List[Dict[str, Any]],
    ) -> DocumentValidationResult:
        indicators: List[str] = []

        # 1. Unreadable or zero-content check
        if word_count < 40 and not is_scanned:
            return DocumentValidationResult(
                is_plausible_manuscript=False,
                document_type="unreadable_or_corrupted",
                confidence=0.95,
                detected_indicators=["Document contains fewer than 40 extractable words"],
                warning_message="The uploaded file contains insufficient extractable text or is unreadable. Please upload a standard digital PDF or DOCX file.",
                extraction_quality="unusable",
            )

        if is_scanned:
            return DocumentValidationResult(
                is_plausible_manuscript=True,
                document_type="research_manuscript",
                confidence=0.7,
                detected_indicators=["Raster scanned document; text density is low"],
                warning_message="Scanned document detected. Digital text and coordinate inspection are provisional until OCR is completed.",
                extraction_quality="low",
            )

        # 2. Check CV vs Academic indicators
        cv_matches = []
        for pattern, label in cls.CV_STRONG_PATTERNS:
            if pattern.search(raw_text):
                cv_matches.append(label)

        academic_matches = []
        for pattern, label in cls.ACADEMIC_STRONG_PATTERNS:
            if pattern.search(raw_text):
                academic_matches.append(label)

        # Count detected academic canonical sections
        detected_canonicals = {s.get("normalized_title") for s in sections if s.get("normalized_title") not in ("abstract", "preamble")}
        has_academic_body = bool({"introduction", "methodology", "results", "conclusion", "references"}.intersection(detected_canonicals))

        # Decision logic for Resume / CV
        if len(cv_matches) >= 3 and not academic_matches and not has_academic_body and page_count <= 3:
            return DocumentValidationResult(
                is_plausible_manuscript=False,
                document_type="resume_or_cv",
                confidence=0.95,
                detected_indicators=cv_matches,
                warning_message=(
                    "Document Validation Notice: The uploaded file appears to be a Curriculum Vitae or Résumé rather than a research manuscript prepared for journal submission. "
                    "Journal guideline verification checks have been marked as unverified or provisional."
                ),
                extraction_quality="moderate",
            )

        # Brief document check
        if page_count == 1 and word_count < 300 and not academic_matches:
            return DocumentValidationResult(
                is_plausible_manuscript=False,
                document_type="brief_document",
                confidence=0.85,
                detected_indicators=["Single-page document with under 300 words and no research headings"],
                warning_message="The uploaded file appears to be an excerpt or brief note rather than a complete manuscript prepared for journal review.",
                extraction_quality="moderate",
            )

        # Standard research manuscript
        quality = "high"
        if len(sections) < 3:
            quality = "moderate"

        return DocumentValidationResult(
            is_plausible_manuscript=True,
            document_type="research_manuscript",
            confidence=0.9,
            detected_indicators=academic_matches or ["Standard document flow"],
            warning_message=None,
            extraction_quality=quality,
        )

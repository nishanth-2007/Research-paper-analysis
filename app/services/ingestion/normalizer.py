import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple


def calculate_file_hash(content: bytes) -> str:
    """Calculates SHA-256 hash for document content to detect duplicates."""
    return hashlib.sha256(content).hexdigest()


SECTION_CANONICAL_MAP = {
    r"\b(abstract)\b": "abstract",
    r"\b(intro|introduction|overview|background)\b": "introduction",
    r"\b(related work|literature review|prior art|previous work)\b": "literature_review",
    r"\b(method|methods|methodology|proposed (method|model|framework|approach)|system architecture|system model)\b": "methodology",
    r"\b(experiment|experiments|evaluation|results|experimental (setup|results|evaluation)|empirical analysis)\b": "results",
    r"\b(discussion|analysis of results)\b": "discussion",
    r"\b(conclusion|conclusions|concluding remarks|future work)\b": "conclusion",
    r"\b(references|bibliography|works cited)\b": "references",
    r"\b(acknowledgment|acknowledgments|acknowledgements)\b": "acknowledgments",
    r"\b(appendix|appendices)\b": "appendix",
}


def normalize_section_title(raw_title: str) -> str:
    """
    Normalizes a section title string to a canonical form.
    E.g., "1. INTRODUCTION", "I. Background" -> "introduction"
    """
    cleaned = re.sub(r"^([0-9]+|[IVXLCDM]+)[\.\:\-\s]+", "", raw_title.strip(), flags=re.IGNORECASE)
    cleaned_lower = cleaned.lower()

    for pattern, canonical in SECTION_CANONICAL_MAP.items():
        if re.search(pattern, cleaned_lower):
            return canonical

    # Clean fallback: lowercase slug
    slug = re.sub(r"[^a-z0-9]+", "_", cleaned_lower).strip("_")
    return slug or "section"


def extract_in_text_citations(text: str, page_number: int = 1) -> List[Dict[str, Any]]:
    """
    Finds numeric citations e.g. [1], [1, 2], [1-3] and author-year citations e.g. (Smith et al., 2020)
    Returns list of parsed citation instances with context snippet.
    """
    citations = []

    # 1. Numeric citations [1], [1, 2], [1-4]
    numeric_pattern = re.compile(r"\[([0-9\s\,\-]+)\]")
    for match in numeric_pattern.finditer(text):
        matched_str = match.group(0)
        inner = match.group(1).strip()
        start = max(0, match.start() - 60)
        end = min(len(text), match.end() + 60)
        snippet = text[start:end].replace("\n", " ").strip()

        # Parse individual indices, e.g., "1, 2" or "1-3"
        parts = re.split(r"[\,\;]\s*", inner)
        for part in parts:
            part = part.strip()
            if "-" in part:
                range_parts = part.split("-")
                if len(range_parts) == 2 and range_parts[0].isdigit() and range_parts[1].isdigit():
                    s, e = int(range_parts[0]), int(range_parts[1])
                    for n in range(s, min(e + 1, s + 50)):
                        citations.append({
                            "key": f"[{n}]",
                            "index": n,
                            "type": "numeric",
                            "page_number": page_number,
                            "snippet": snippet,
                        })
                    continue
            if part.isdigit():
                citations.append({
                    "key": f"[{part}]",
                    "index": int(part),
                    "type": "numeric",
                    "page_number": page_number,
                    "snippet": snippet,
                })

    # 2. Author-year citations (Smith et al., 2021) or (Smith and Jones, 2019)
    author_year_pattern = re.compile(r"\(([A-Z][a-zA-Z\s\.\&]+(?:et al\.?)?,\s*(?:19|20)\d{2}[a-z]?)\)")
    for match in author_year_pattern.finditer(text):
        citation_str = match.group(1).strip()
        start = max(0, match.start() - 60)
        end = min(len(text), match.end() + 60)
        snippet = text[start:end].replace("\n", " ").strip()

        citations.append({
            "key": f"({citation_str})",
            "type": "author_year",
            "page_number": page_number,
            "snippet": snippet,
        })

    return citations


def parse_reference_entries(references_text: str) -> List[Dict[str, Any]]:
    """
    Parses raw bibliography text into structured entries.
    Identifies index, authors, year, title, and flags malformed items.
    """
    entries = []
    lines = [line.strip() for line in references_text.split("\n") if line.strip()]

    # Check if numbered [1], [2] or 1., 2.
    current_entry = ""
    current_index = 1

    numbered_start_pattern = re.compile(r"^(\[(\d+)\]|\b(\d+)\.)\s*(.*)")

    for line in lines:
        match = numbered_start_pattern.match(line)
        if match:
            if current_entry:
                entries.append(_structure_single_reference(current_entry, current_index))
                current_index += 1
            idx_found = match.group(2) or match.group(3)
            current_index = int(idx_found)
            current_entry = match.group(4)
        else:
            if current_entry:
                current_entry += " " + line
            else:
                current_entry = line

    if current_entry:
        entries.append(_structure_single_reference(current_entry, current_index))

    # If no numbered pattern found, split by double newlines or bullet lines
    if not entries and len(references_text.strip()) > 10:
        raw_items = [item.strip() for item in re.split(r"\n\s*\n", references_text) if item.strip()]
        for i, item in enumerate(raw_items, 1):
            entries.append(_structure_single_reference(item, i))

    return entries


def _structure_single_reference(raw_text: str, index: int) -> Dict[str, Any]:
    # Extract year (e.g. 1999, 2024)
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", raw_text)
    detected_year = year_match.group(1) if year_match else None

    # Extract DOI
    doi_match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", raw_text)
    detected_doi = doi_match.group(1) if doi_match else None

    # Check for authors heuristic (usually first part before quotes or title)
    parts = raw_text.split('"')
    detected_title = None
    if len(parts) >= 3:
        detected_title = parts[1].strip()

    # Heuristic for malformed: too short (< 15 chars) or missing author/year structure
    is_malformed = len(raw_text) < 20 or (not detected_year and not detected_doi and len(raw_text) < 40)

    return {
        "index": index,
        "raw_text": raw_text.strip(),
        "detected_year": detected_year,
        "detected_doi": detected_doi,
        "detected_title": detected_title,
        "is_malformed": is_malformed,
    }

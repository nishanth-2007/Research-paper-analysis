from typing import Dict, Any


DEFAULT_CATEGORY_WEIGHTS: Dict[str, Dict[str, Any]] = {
    "citation_reference": {
        "label": "Citation & Reference Integrity",
        "weight": 0.25,
    },
    "compliance_formatting": {
        "label": "Journal Guidelines & Formatting",
        "weight": 0.20,
    },
    "manuscript_completeness": {
        "label": "Manuscript Completeness & Structure",
        "weight": 0.20,
    },
    "methodology_rigor": {
        "label": "Methodology Rigor & Technical Contribution",
        "weight": 0.20,
    },
    "scope_alignment": {
        "label": "Scope Alignment & Literature Context",
        "weight": 0.15,
    },
}

SEVERITY_DEDUCTION_TABLE: Dict[str, float] = {
    "critical": 30.0,
    "major": 18.0,
    "moderate": 10.0,
    "minor": 4.0,
    "info": 0.0,
}

UNVERIFIED_CHECK_PENALTY: float = 12.0

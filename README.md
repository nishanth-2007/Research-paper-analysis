# Research Paper Automation & Journal Readiness Platform

A production-minded, modular backend for automated research manuscript verification, guideline compliance checking, and explainable journal-readiness evaluation.

---

## 1. System Architecture

```
                    ┌─────────────────────────┐
                    │  Client / UI (Frontend) │
                    └────────────┬────────────┘
                                 │ HTTP (RESTful JSON / Binary)
                                 ▼
                    ┌─────────────────────────┐
                    │   FastAPI API Layer     │
                    │  (/api/v1/manuscripts,  │
                    │   /api/v1/journals,     │
                    │   /api/v1/analysis)     │
                    └────────────┬────────────┘
                                 │
           ┌─────────────────────┴─────────────────────┐
           ▼                                           ▼
┌───────────────────────┐                 ┌─────────────────────────┐
│ Object Storage Layer  │                 │   PostgreSQL / SQLite   │
│ (Local / S3-Backend)  │                 │  (SQLAlchemy 2.x ORM &  │
│  - Original PDF/DOCX  │                 │    Alembic Migrations)  │
│  - Generated Reports  │                 └─────────────────────────┘
└──────────┬────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Central Analysis Orchestrator                  │
│                                                                  │
│  1. Document Ingestion & Normalizer (PyMuPDF / python-docx)      │
│     - SHA-256 deduplication, layout metrics, scanned detector   │
│     - Section boundary segmentation, citation & ref extractor    │
│                                                                  │
│  2. Parallel Multi-Engine Verification:                          │
│     ├── Deterministic Verification Engine                        │
│     │   - Citation-to-reference matching ([X] vs bibliography)   │
│     │   - Uncited bibliography items, duplicate DOIs             │
│     │   - Core sections (IMRAD) & abstract word limits           │
│     │   - Sequential figure/table numbering & text references   │
│     │   - Typography (font size pt), page limits & layout        │
│     │                                                            │
│     ├── Journal Knowledge Base & RAG Engine                      │
│     │   - Publisher-verified guidelines (IEEE, Nature, Elsevier) │
│     │   - Strict journal metadata isolation (prevents leakage)   │
│     │   - Citation style conformity (IEEE brackets vs APA)       │
│     │   - Mandatory statements (Data & Code Availability)        │
│     │                                                            │
│     └── LLM Academic Evaluation Engine                           │
│         - Qualitative academic rigor, research question clarity  │
│         - Methodological completeness & threats to validity      │
│         - Preliminary novelty analysis (guarded by disclaimer)   │
│         - Prompt injection containment & strict Pydantic schemas │
│                                                                  │
│  3. Finding Aggregator & Deduplicator                            │
│  4. Explainable Readiness Scoring Engine (0-100 deterministic)   │
│  5. Report Generation & Exporter (JSON, ReportLab PDF, DOCX)     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Common Finding Schema (Shared by All Engines)

Every check across all evaluation engines outputs a standardized `Finding`:

```json
{
  "finding_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "rule_id": "DETERM_CIT_MISSING_REF_99",
  "engine": "deterministic",
  "category": "citation_reference",
  "status": "fail",
  "severity": "critical",
  "title": "In-Text Citation [99] Has No Matching Bibliography Entry",
  "expected_requirement": "Every in-text citation must correspond to an entry in the References list.",
  "actual_observation": "Citation [99] appears in text on page 1, but reference #99 does not exist.",
  "evidence": "Here we cite [1] and non-existent reference [99].",
  "source_location": {
    "page_number": 1,
    "section_name": "Introduction"
  },
  "guideline_source": {
    "publisher": "IEEE",
    "guideline_name": "IEEE Access Guidelines",
    "source_url": "https://ieeeaccess.ieee.org/guide-for-authors/",
    "verified_on": "2026-09-19"
  },
  "confidence": 1.0,
  "suggested_correction": "Add reference #99 to the bibliography or update citation tag.",
  "is_provisional": false
}
```

---

## 3. Database Schema

The normalized relational database schema includes 16 entities:

| Table | Purpose |
|---|---|
| `users` | Multi-tenant user accounts with password hashing |
| `journals` | Verified academic journals, publishers, and scopes |
| `guideline_versions` | Versioned submission guidelines with verification dates and provenance |
| `journal_rules` | Discrete, versioned journal compliance rules and parameters |
| `guideline_chunks` | Semantic text passages with vector embeddings (`pgvector`) |
| `manuscripts` | Top-level manuscript containers owned by users |
| `manuscript_versions` | Specific uploaded files with SHA-256 hash, page/word counts, and scanned flags |
| `document_sections` | Extracted sections (Abstract, Intro, Methods, Results, etc.) with page boundaries |
| `references` | Extracted bibliography items with parsed authors, year, title, and DOI |
| `citations` | In-text citations linked to matching reference records |
| `analysis_jobs` | Background asynchronous processing jobs with progress % and status |
| `analysis_runs` | Individual evaluation engine runs with execution timestamps |
| `verification_results` | Granular findings produced by deterministic and RAG checks |
| `academic_assessments` | Qualitative peer-review criteria evaluations (Methodology, novelty, rigor) |
| `readiness_scores` | Deterministic 0–100 scores, category breakdowns, and calculation formulas |
| `generated_reports` | Generated JSON reports and storage keys for downloadable PDF/DOCX files |

---

## 4. API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health status and active configuration |
| `GET` | `/api/v1/db-health` | Database connection and engine diagnostics |
| `GET` | `/api/v1/journals` | List all verified journals, publishers, and scopes |
| `GET` | `/api/v1/journals/{journal_id}/guidelines` | Get official guideline version, rules, and semantic chunks |
| `POST` | `/api/v1/manuscripts/upload` | Upload PDF or DOCX file (extracts text, sections, refs, layout) |
| `GET` | `/api/v1/manuscripts` | List manuscripts owned by the authenticated user |
| `GET` | `/api/v1/manuscripts/{id}` | Retrieve manuscript details and all version histories |
| `GET` | `/api/v1/manuscripts/{id}/versions` | List revisions and extraction metadata |
| `POST` | `/api/v1/manuscripts/{id}/analyze` | **Queue asynchronous analysis** (returns HTTP 202 + `status_url`) |
| `GET` | `/api/v1/analysis/{analysis_id}` | Check job progress (0% → 100%) and current execution step |
| `GET` | `/api/v1/analysis/{analysis_id}/results` | Retrieve detailed findings from all 3 evaluation engines |
| `GET` | `/api/v1/analysis/{analysis_id}/report` | Retrieve complete explainable readiness report (JSON) |
| `GET` | `/api/v1/analysis/{analysis_id}/export?format=pdf` | **Download publication-readiness PDF audit report** |
| `GET` | `/api/v1/analysis/{analysis_id}/export?format=docx` | **Download publication-readiness Word DOCX audit report** |

---

## 5. Explainable Readiness Scoring Algorithm

1. **Category Weighting**:
   - `citation_reference`: 25%
   - `compliance_formatting`: 20%
   - `manuscript_completeness`: 20%
   - `methodology_rigor`: 20%
   - `scope_alignment`: 15%
   *(Sum = 100%)*

2. **Deterministic Deductions**:
   - `CRITICAL` failure: -30 points from category
   - `MAJOR` failure: -18 points from category
   - `MODERATE` warning/failure: -10 points from category
   - `MINOR` warning/failure: -4 points from category
   - `UNABLE_TO_VERIFY`: -12 points provisional penalty (marks category `is_provisional=True`)

3. **Readiness Tiers**:
   - **85.0 – 100.0**: Ready for Submission (High Confidence)
   - **70.0 – 84.9**: Minor Revisions Required
   - **50.0 – 69.9**: Substantial Revisions Required
   - **< 50.0**: Early Draft / Critical Deficiencies

*Note: The score is an indicator of technical guideline compliance and structural readiness. It is not an acceptance guarantee.*

---

## 6. How to Run Locally

### Prerequisites
- Python 3.10+
- SQLite (included by default) or PostgreSQL 15+

### Installation & Environment Setup
```bash
# Clone and enter directory
cd "d:\Research paper analysis"

# Install production dependencies
pip install -r requirements.txt

# Create .env from template
copy .env.example .env
```

### Run Database Migrations
```bash
python -m alembic upgrade head
```

### Start Backend Server
```bash
python main.py
# Or using uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Run Automated Tests
```bash
python -m pytest -v
```

---

## 7. Verification Capabilities & Known Limitations

### Implemented Capabilities
- **Citation cross-referencing**: detects missing bibliography items for in-text citations, uncited references, and duplicate DOIs.
- **Structural section validation**: detects missing IMRAD sections (Abstract, Intro, Methods, Results, Conclusion).
- **Word count constraints**: verifies abstract and section lengths against journal-specific boundaries.
- **Figure & table verification**: sequential numbering check, caption detection, and in-text mention tracking.
- **Layout & typography analysis**: inspects average font size, page counts, and page margins via PyMuPDF.
- **Scanned document detection**: detects raster scanned PDFs without text streams, prevents false passes, and marks results as provisional.
- **RAG guideline isolation**: searches only within the targeted journal’s rules and chunks to prevent cross-journal hallucination.
- **Prompt injection defense**: fences manuscript text in `<untrusted_manuscript_content>` XML tags with system-level instruction guards.
- **Export capabilities**: generates complete PDF (ReportLab) and DOCX (python-docx) reports.

### Known Limitations
- OCR for fully rasterized scanned PDFs requires Tesseract or cloud vision OCR backend (flagged as `UNABLE_TO_VERIFY` with provisional score).
- Camera-ready column formatting (e.g., exact 2-column IEEE gutter spacing) is checked via coordinate bounding box heuristics rather than full DTP rendering.

import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.manuscript import (
    Manuscript,
    ManuscriptVersion,
    DocumentSection,
    Reference,
    Citation,
)
from app.schemas.manuscript import (
    UploadManuscriptResponse,
    ManuscriptListItem,
    ManuscriptDetail,
    ManuscriptVersionDetail,
)
from app.services.storage import get_storage_service
from app.services.ingestion.extractor import DocumentExtractor
from app.api.deps import get_current_user

router = APIRouter(prefix="/manuscripts", tags=["Manuscripts"])


@router.post("/upload", response_model=UploadManuscriptResponse, status_code=status.HTTP_201_CREATED)
async def upload_manuscript(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ingest, validate, extract, and store a manuscript (PDF or DOCX).
    """
    # 1. Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats are: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    # 2. Read content and validate size
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed upload size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    # 3. Save raw file into storage service
    storage = get_storage_service()
    storage_path = storage.save_file(
        content=content,
        filename=file.filename,
        subfolder="manuscripts",
    )

    # 4. Extract document structure and metadata
    try:
        extracted = DocumentExtractor.extract_document(content=content, filename=file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Document parsing error: {str(e)}",
        )

    final_title = title or extracted.title or file.filename

    # 5. Check if manuscript already exists for user by hash or create new
    existing_version = (
        db.query(ManuscriptVersion)
        .join(Manuscript)
        .filter(
            Manuscript.user_id == current_user.id,
            ManuscriptVersion.file_hash_sha256 == extracted.file_hash,
        )
        .first()
    )

    if existing_version:
        # Detected duplicate upload
        manuscript = existing_version.manuscript
        version_num = len(manuscript.versions) + 1
    else:
        manuscript = Manuscript(
            user_id=current_user.id,
            title=final_title,
        )
        db.add(manuscript)
        db.flush()
        version_num = 1

    # 6. Create ManuscriptVersion
    version = ManuscriptVersion(
        manuscript_id=manuscript.id,
        version_number=version_num,
        original_filename=file.filename,
        file_type=ext,
        file_size_bytes=len(content),
        file_hash_sha256=extracted.file_hash,
        storage_path=storage_path,
        page_count=extracted.page_count,
        word_count=extracted.word_count,
        is_scanned_pdf=extracted.is_scanned,
        ocr_required=extracted.ocr_required,
        extraction_metadata={
            "layout": extracted.layout_metrics,
            "figures_count": len(extracted.figures),
            "tables_count": len(extracted.tables),
        },
    )
    db.add(version)
    db.flush()

    # 7. Persist DocumentSections
    for s in extracted.sections:
        sec_row = DocumentSection(
            manuscript_version_id=version.id,
            section_order=s["section_order"],
            title=s["title"],
            normalized_title=s["normalized_title"],
            content=s["content"],
            word_count=s["word_count"],
            start_page=s.get("start_page"),
            end_page=s.get("end_page"),
        )
        db.add(sec_row)

    # 8. Persist References
    ref_map = {}
    for r in extracted.references:
        ref_row = Reference(
            manuscript_version_id=version.id,
            reference_index=r["index"],
            raw_text=r["raw_text"],
            detected_authors=r.get("detected_authors"),
            detected_title=r.get("detected_title"),
            detected_year=r.get("detected_year"),
            detected_doi=r.get("detected_doi"),
            is_malformed=r.get("is_malformed", False),
        )
        db.add(ref_row)
        db.flush()
        ref_map[r["index"]] = ref_row.id

    # 9. Persist Citations
    for c in extracted.citations:
        matched_id = ref_map.get(c.get("index")) if c.get("index") else None
        cit_row = Citation(
            manuscript_version_id=version.id,
            citation_key=c["key"],
            context_snippet=c.get("snippet"),
            page_number=c.get("page_number"),
            matched_reference_id=matched_id,
        )
        db.add(cit_row)

    db.commit()

    return UploadManuscriptResponse(
        manuscript_id=manuscript.id,
        version_id=version.id,
        version_number=version.version_number,
        title=manuscript.title,
        original_filename=version.original_filename,
        file_size_bytes=version.file_size_bytes,
        file_hash_sha256=version.file_hash_sha256,
        page_count=version.page_count,
        word_count=version.word_count,
        is_scanned_pdf=version.is_scanned_pdf,
        ocr_required=version.ocr_required,
    )


@router.get("", response_model=List[ManuscriptListItem])
def list_manuscripts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all manuscripts owned by the authenticated researcher."""
    manuscripts = (
        db.query(Manuscript)
        .filter(Manuscript.user_id == current_user.id)
        .order_by(Manuscript.updated_at.desc())
        .all()
    )

    items = []
    for m in manuscripts:
        latest_ver = max([v.version_number for v in m.versions], default=1)
        items.append(ManuscriptListItem(
            id=m.id,
            title=m.title,
            latest_version_number=latest_ver,
            created_at=m.created_at,
            updated_at=m.updated_at,
        ))
    return items


@router.get("/{manuscript_id}", response_model=ManuscriptDetail)
def get_manuscript(
    manuscript_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve manuscript details with all versions and sections."""
    manuscript = (
        db.query(Manuscript)
        .filter(Manuscript.id == manuscript_id, Manuscript.user_id == current_user.id)
        .first()
    )
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manuscript '{manuscript_id}' not found.",
        )
    return manuscript


@router.get("/{manuscript_id}/versions", response_model=List[ManuscriptVersionDetail])
def list_manuscript_versions(
    manuscript_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all revision versions for a specific manuscript."""
    manuscript = (
        db.query(Manuscript)
        .filter(Manuscript.id == manuscript_id, Manuscript.user_id == current_user.id)
        .first()
    )
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manuscript '{manuscript_id}' not found.",
        )
    return manuscript.versions


@router.post("/export-docx")
def export_manuscript_docx(
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate and download publication-formatted Microsoft Word (.docx) manuscript."""
    from fastapi import Response
    from app.services.export.manuscript_exporter import ManuscriptDocumentExporter

    try:
        docx_bytes = ManuscriptDocumentExporter.generate_docx(payload)
        journal_tag = payload.get("target_journal_id") or "formatted"
        filename = f"manuscript_{journal_tag}.docx"
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DOCX manuscript: {str(e)}",
        )


@router.post("/export-pdf")
def export_manuscript_pdf(
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate and download publication-formatted PDF manuscript."""
    from fastapi import Response
    from app.services.export.manuscript_exporter import ManuscriptDocumentExporter

    try:
        pdf_bytes = ManuscriptDocumentExporter.generate_pdf(payload)
        journal_tag = payload.get("target_journal_id") or "formatted"
        filename = f"manuscript_{journal_tag}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF manuscript: {str(e)}",
        )


@router.post("/similarity-audit")
def audit_manuscript_similarity(
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    """
    Run authentic N-gram shingling & similarity audit on manuscript text.
    Returns similarity index, category breakdown, section rates, and flagged fragments.
    """
    from app.services.engines.plagiarism import PlagiarismSimilarityEngine

    try:
        exclude_references = payload.get("exclude_references", True)
        exclude_quotes = payload.get("exclude_quotes", True)
        min_words_threshold = payload.get("min_words_threshold", 6)

        report = PlagiarismSimilarityEngine.analyze(
            manuscript_data=payload,
            exclude_references=exclude_references,
            exclude_quotes=exclude_quotes,
            min_words_threshold=min_words_threshold,
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate similarity audit: {str(e)}",
        )


from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.journal import Journal, GuidelineVersion, JournalRule, GuidelineChunk
from app.schemas.journal import JournalSummary, JournalDetail, GuidelineVersionSchema
from app.services.engines.rag.knowledge_base import DEFAULT_JOURNAL_SEEDS, prepare_seed_embeddings

router = APIRouter(prefix="/journals", tags=["Journals & Guidelines"])


def ensure_journals_seeded(db: Session):
    seeds = prepare_seed_embeddings(DEFAULT_JOURNAL_SEEDS)
    for s in seeds:
        j = db.query(Journal).filter(Journal.id == s["id"]).first()
        if not j:
            j = Journal(
                id=s["id"],
                name=s["name"],
                publisher=s["publisher"],
                scope=s["scope"],
                citation_style=s["citation_style"],
                official_url=s["official_url"],
                is_active=True,
            )
            db.add(j)
            db.flush()

            gv = GuidelineVersion(
                journal_id=j.id,
                version_tag=s["version_tag"],
                provenance=s["provenance"],
                is_current=True,
            )
            db.add(gv)
            db.flush()

            for r in s.get("rules", []):
                jr = JournalRule(
                    guideline_version_id=gv.id,
                    rule_code=r["rule_code"],
                    category=r["category"],
                    requirement_description=r["requirement_description"],
                    rule_parameters=r.get("rule_parameters"),
                    severity=r.get("severity", "major"),
                )
                db.add(jr)

            for c in s.get("chunks", []):
                gc = GuidelineChunk(
                    guideline_version_id=gv.id,
                    chunk_index=c["chunk_index"],
                    section_heading=c.get("section_heading"),
                    content=c["content"],
                    source_url=c.get("source_url"),
                    embedding=c.get("embedding"),
                )
                db.add(gc)
        else:
            if j.official_url != s["official_url"]:
                j.official_url = s["official_url"]
            gv = db.query(GuidelineVersion).filter(GuidelineVersion.journal_id == j.id, GuidelineVersion.is_current == True).first()
            if gv:
                for r in s.get("rules", []):
                    jr = db.query(JournalRule).filter(JournalRule.guideline_version_id == gv.id, JournalRule.rule_code == r["rule_code"]).first()
                    if jr:
                        jr.rule_parameters = r.get("rule_parameters")
                        jr.requirement_description = r["requirement_description"]
                    else:
                        jr = JournalRule(
                            guideline_version_id=gv.id,
                            rule_code=r["rule_code"],
                            category=r["category"],
                            requirement_description=r["requirement_description"],
                            rule_parameters=r.get("rule_parameters"),
                            severity=r.get("severity", "major"),
                        )
                        db.add(jr)
    db.commit()


@router.get("", response_model=List[JournalSummary])
def list_journals(db: Session = Depends(get_db)):
    """Retrieve all verified academic journals in the knowledge base."""
    ensure_journals_seeded(db)
    journals = db.query(Journal).filter(Journal.is_active == True).all()
    return journals


@router.get("/{journal_id}/guidelines", response_model=GuidelineVersionSchema)
def get_journal_guidelines(journal_id: str, db: Session = Depends(get_db)):
    """Retrieve official submission guidelines, rules, and semantic chunks for a journal."""
    ensure_journals_seeded(db)
    journal = db.query(Journal).filter(Journal.id == journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal '{journal_id}' not found.",
        )

    current_gv = (
        db.query(GuidelineVersion)
        .filter(GuidelineVersion.journal_id == journal_id, GuidelineVersion.is_current == True)
        .first()
    )
    if not current_gv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active guideline version found for journal '{journal_id}'.",
        )

    return current_gv

from app.models.journal import Journal, GuidelineVersion
from app.services.engines.rag.retriever import GuidelineRetriever
from app.services.engines.rag.engine import RAGEngine
from app.services.ingestion.extractor import DocumentExtractor
from app.schemas.common import CheckStatus


def test_guideline_retriever_metadata_isolation(db_session):
    ieee_gv = db_session.query(GuidelineVersion).filter(GuidelineVersion.journal_id == "ieee-access").first()
    nature_gv = db_session.query(GuidelineVersion).filter(GuidelineVersion.journal_id == "nature-comms").first()

    assert ieee_gv is not None
    assert nature_gv is not None

    # Query IEEE guideline version
    ieee_chunks = GuidelineRetriever.retrieve_relevant_chunks(
        query="data availability statement reproducibility",
        guideline_version=ieee_gv,
        top_k=5,
    )
    # Ensure every returned chunk belongs strictly to IEEE
    for c in ieee_chunks:
        matching_chunk = [chk for chk in ieee_gv.chunks if chk.id == c["chunk_id"]]
        assert len(matching_chunk) == 1

    # Query Nature guideline version
    nature_chunks = GuidelineRetriever.retrieve_relevant_chunks(
        query="data availability statement mandatory reporting",
        guideline_version=nature_gv,
        top_k=5,
    )
    for c in nature_chunks:
        matching_chunk = [chk for chk in nature_gv.chunks if chk.id == c["chunk_id"]]
        assert len(matching_chunk) == 1


def test_rag_engine_evaluation_with_provenance(db_session, valid_pdf_bytes):
    ieee_gv = db_session.query(GuidelineVersion).filter(GuidelineVersion.journal_id == "ieee-access").first()
    doc = DocumentExtractor.extract_document(valid_pdf_bytes, "valid.pdf")

    rag = RAGEngine()
    result = rag.evaluate(document=doc, guideline_version=ieee_gv)

    assert result.status == "completed"
    assert len(result.findings) >= 2

    # Check that findings contain official guideline citations
    findings_with_source = [f for f in result.findings if f.guideline_source is not None]
    assert len(findings_with_source) >= 1
    src = findings_with_source[0].guideline_source
    assert src.publisher == "IEEE"
    assert src.source_url is not None


def test_rag_engine_mandatory_statement_violation(db_session, flawed_pdf_bytes):
    nature_gv = db_session.query(GuidelineVersion).filter(GuidelineVersion.journal_id == "nature-comms").first()
    doc = DocumentExtractor.extract_document(flawed_pdf_bytes, "flawed.pdf")

    rag = RAGEngine()
    result = rag.evaluate(document=doc, guideline_version=nature_gv)

    # Nature requires Data Availability statement; flawed doc lacks it -> should FAIL
    data_findings = [f for f in result.findings if "DATA_AVAILABILITY" in f.rule_id]
    assert len(data_findings) >= 1
    assert data_findings[0].status == CheckStatus.FAIL

import time
from typing import Optional, Dict, Any, List
from app.schemas.common import (
    EngineResult,
    EngineType,
    Finding,
    CheckStatus,
    Severity,
    GuidelineSource,
    SourceLocation,
)
from app.services.engines.base import BaseEvaluationEngine
from app.services.ingestion.extractor import ExtractedDocument
from app.models.journal import GuidelineVersion
from app.services.engines.rag.retriever import GuidelineRetriever


class RAGEngine(BaseEvaluationEngine):
    def evaluate(
        self,
        document: ExtractedDocument,
        guideline_version: Optional[GuidelineVersion] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> EngineResult:
        start_time = time.perf_counter()
        findings: List[Finding] = []

        if not guideline_version:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            findings.append(Finding(
                rule_id="RAG_NO_JOURNAL_SPECIFIED",
                engine=EngineType.RAG_KNOWLEDGE,
                category="scope_alignment",
                status=CheckStatus.WARNING,
                severity=Severity.INFO,
                title="No Target Journal Selected for RAG Verification",
                expected_requirement="Select a specific target journal (e.g., IEEE Access, Nature Communications) to evaluate publisher-specific compliance.",
                actual_observation="Analysis executed under generic academic manuscript conventions.",
                is_provisional=False,
                confidence=1.0,
            ))
            return EngineResult(
                engine=EngineType.RAG_KNOWLEDGE,
                execution_time_ms=round(elapsed_ms, 2),
                status="completed",
                findings=findings,
                summary={"journal_selected": False},
            )

        journal = guideline_version.journal
        prov = guideline_version.provenance or {}
        verified_on = prov.get("last_verified", "2026-09-19")

        # 1. RAG Scope Alignment Check
        scope_query = f"manuscript title {document.title} scope domains keywords topic"
        retrieved_scope_chunks = GuidelineRetriever.retrieve_relevant_chunks(
            query=scope_query,
            guideline_version=guideline_version,
            top_k=2,
        )

        scope_terms = journal.scope or []
        doc_text_lower = document.raw_text.lower()
        matched_scope_terms = [t for t in scope_terms if t.lower() in doc_text_lower]

        primary_scope_chunk = retrieved_scope_chunks[0] if retrieved_scope_chunks else None
        scope_guideline_source = GuidelineSource(
            publisher=journal.publisher,
            guideline_name=f"{journal.name} Submission Guidelines",
            section_title=primary_scope_chunk["section_heading"] if primary_scope_chunk else "Scope",
            source_url=primary_scope_chunk["source_url"] if primary_scope_chunk else journal.official_url,
            verified_on=str(verified_on),
        )

        if len(matched_scope_terms) >= 1:
            findings.append(Finding(
                rule_id="RAG_SCOPE_ALIGNED",
                engine=EngineType.RAG_KNOWLEDGE,
                category="scope_alignment",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                title=f"Manuscript Scope Aligns with {journal.name}",
                expected_requirement=f"Manuscript subject matter must fall within {journal.name}'s designated scope: {', '.join(scope_terms[:4])}.",
                actual_observation=f"Matched recognized topical keywords in text: {', '.join(matched_scope_terms)}.",
                evidence=primary_scope_chunk["content"] if primary_scope_chunk else None,
                guideline_source=scope_guideline_source,
                confidence=0.9,
            ))
        else:
            findings.append(Finding(
                rule_id="RAG_SCOPE_POTENTIAL_MISMATCH",
                engine=EngineType.RAG_KNOWLEDGE,
                category="scope_alignment",
                status=CheckStatus.WARNING,
                severity=Severity.MAJOR,
                title=f"Potential Scope Discrepancy with {journal.name}",
                expected_requirement=f"{journal.name} prioritizes research in {', '.join(scope_terms[:4])}.",
                actual_observation=f"Limited explicit mention of journal core domain keywords ({', '.join(scope_terms[:3])}) was identified in the title and abstract.",
                evidence=primary_scope_chunk["content"] if primary_scope_chunk else None,
                guideline_source=scope_guideline_source,
                suggested_correction=f"Clarify relevance and contributions to {journal.name} readership in the Introduction.",
                confidence=0.75,
            ))

        # 2. Citation Style Check via Retrieved Style Guidelines
        retrieved_citation_chunks = GuidelineRetriever.retrieve_relevant_chunks(
            query="citation style references numbering square brackets author year format",
            guideline_version=guideline_version,
            top_k=2,
        )
        cit_chunk = retrieved_citation_chunks[0] if retrieved_citation_chunks else None
        cit_guideline_source = GuidelineSource(
            publisher=journal.publisher,
            guideline_name=f"{journal.name} Citation Standards",
            section_title=cit_chunk["section_heading"] if cit_chunk else "Citations",
            source_url=cit_chunk["source_url"] if cit_chunk else journal.official_url,
            verified_on=str(verified_on),
        )

        # Check IEEE numbered bracket requirement vs author-year
        has_numeric = any(c.get("type") == "numeric" for c in document.citations)
        has_author_year = any(c.get("type") == "author_year" for c in document.citations)

        cit_style_lower = (journal.citation_style or "").lower()
        if "IEEE" in journal.name:
            if has_author_year and not has_numeric:
                findings.append(Finding(
                    rule_id="RAG_IEEE_CITATION_STYLE_VIOLATION",
                    engine=EngineType.RAG_KNOWLEDGE,
                    category="citation_reference",
                    status=CheckStatus.FAIL,
                    severity=Severity.CRITICAL,
                    title="Citation Format Incompatible with IEEE Access Guidelines",
                    expected_requirement="IEEE style mandates numbered bracketed citations [1], [2], ordered sequentially.",
                    actual_observation="Detected Harvard/Author-Year citations (e.g. '(Author, 2021)') without IEEE bracketed numeric indexing.",
                    evidence=cit_chunk["content"] if cit_chunk else None,
                    guideline_source=cit_guideline_source,
                    suggested_correction="Convert citations and reference list to IEEE numbered bracketed format [1], [2].",
                    confidence=0.98,
                ))
            elif has_numeric:
                findings.append(Finding(
                    rule_id="RAG_IEEE_CITATION_STYLE_COMPLIANT",
                    engine=EngineType.RAG_KNOWLEDGE,
                    category="citation_reference",
                    status=CheckStatus.PASS,
                    severity=Severity.INFO,
                    title="Citation Style Conforms to IEEE Guidelines",
                    expected_requirement="IEEE requires bracketed numeric citations [1].",
                    actual_observation="In-text citations correctly follow bracketed numeric scheme.",
                    guideline_source=cit_guideline_source,
                    confidence=1.0,
                ))
        elif "author-year" in cit_style_lower or "harvard" in cit_style_lower:
            if has_numeric and not has_author_year:
                findings.append(Finding(
                    rule_id="RAG_CITATION_STYLE_VIOLATION",
                    engine=EngineType.RAG_KNOWLEDGE,
                    category="citation_reference",
                    status=CheckStatus.FAIL,
                    severity=Severity.MAJOR,
                    title=f"Citation Format Incompatible with {journal.name} Guidelines",
                    expected_requirement=f"{journal.name} guidelines specify {journal.citation_style}.",
                    actual_observation="Detected numeric bracketed citations instead of the expected Author-Year (e.g. '(Smith et al., 2024)') format.",
                    evidence=cit_chunk["content"] if cit_chunk else None,
                    guideline_source=cit_guideline_source,
                    suggested_correction=f"Convert citations and reference entries to Author-Year format per {journal.name} standards.",
                    confidence=0.95,
                ))
            elif has_author_year:
                findings.append(Finding(
                    rule_id="RAG_CITATION_STYLE_COMPLIANT",
                    engine=EngineType.RAG_KNOWLEDGE,
                    category="citation_reference",
                    status=CheckStatus.PASS,
                    severity=Severity.INFO,
                    title=f"Citation Style Conforms to {journal.name} Guidelines",
                    expected_requirement=f"{journal.name} specifies {journal.citation_style}.",
                    actual_observation="In-text citations correctly follow Author-Year scheme.",
                    guideline_source=cit_guideline_source,
                    confidence=1.0,
                ))
        elif any(kw in cit_style_lower for kw in ["numbered", "bracket", "vancouver", "aps", "sequential"]):
            if has_author_year and not has_numeric:
                findings.append(Finding(
                    rule_id="RAG_CITATION_STYLE_VIOLATION",
                    engine=EngineType.RAG_KNOWLEDGE,
                    category="citation_reference",
                    status=CheckStatus.FAIL,
                    severity=Severity.MAJOR,
                    title=f"Citation Format Incompatible with {journal.name} Guidelines",
                    expected_requirement=f"{journal.name} mandates {journal.citation_style}.",
                    actual_observation=f"Detected Author-Year citations without sequential numbered brackets required by {journal.name}.",
                    evidence=cit_chunk["content"] if cit_chunk else None,
                    guideline_source=cit_guideline_source,
                    suggested_correction=f"Convert citations and bibliography to numbered format per {journal.name} guidelines.",
                    confidence=0.95,
                ))
            elif has_numeric:
                findings.append(Finding(
                    rule_id="RAG_CITATION_STYLE_COMPLIANT",
                    engine=EngineType.RAG_KNOWLEDGE,
                    category="citation_reference",
                    status=CheckStatus.PASS,
                    severity=Severity.INFO,
                    title=f"Citation Style Conforms to {journal.name} Guidelines",
                    expected_requirement=f"{journal.name} specifies {journal.citation_style}.",
                    actual_observation="In-text citations correctly follow numbered scheme.",
                    guideline_source=cit_guideline_source,
                    confidence=1.0,
                ))

        # 3. Mandatory Statement Checks from Guidelines (e.g. Data Availability / Competing Interest)
        for rule in guideline_version.rules:
            if "DATA_AVAILABILITY" in rule.rule_code:
                data_chunks = GuidelineRetriever.retrieve_relevant_chunks(
                    query="data availability statement repository accession",
                    guideline_version=guideline_version,
                    top_k=1,
                )
                chunk_src = data_chunks[0] if data_chunks else None
                g_src = GuidelineSource(
                    publisher=journal.publisher,
                    guideline_name=f"{journal.name} Policy",
                    section_title=chunk_src["section_heading"] if chunk_src else "Data Policy",
                    source_url=chunk_src["source_url"] if chunk_src else journal.official_url,
                    verified_on=str(verified_on),
                )

                has_data_stmt = bool(re_search_term(doc_text_lower, ["data availability", "data access", "availability of data"]))
                if not has_data_stmt:
                    findings.append(Finding(
                        rule_id=rule.rule_code,
                        engine=EngineType.RAG_KNOWLEDGE,
                        category="manuscript_completeness",
                        status=CheckStatus.FAIL,
                        severity=Severity.CRITICAL if "nature" in journal.id else Severity.MODERATE,
                        title=f"Missing Mandatory Statement: Data Availability ({journal.name})",
                        expected_requirement=rule.requirement_description,
                        actual_observation="No explicit 'Data Availability' section or statement was identified in the manuscript.",
                        evidence=chunk_src["content"] if chunk_src else None,
                        guideline_source=g_src,
                        suggested_correction="Add an explicit 'Data Availability Statement' stating where raw data and artifacts are accessible.",
                        confidence=0.95,
                    ))
                else:
                    findings.append(Finding(
                        rule_id=f"{rule.rule_code}_PASS",
                        engine=EngineType.RAG_KNOWLEDGE,
                        category="manuscript_completeness",
                        status=CheckStatus.PASS,
                        severity=Severity.INFO,
                        title="Data Availability Statement Verified",
                        expected_requirement=rule.requirement_description,
                        actual_observation="Data availability statement detected in manuscript.",
                        guideline_source=g_src,
                        confidence=0.95,
                    ))

            elif "CONFLICT_INTEREST" in rule.rule_code:
                has_coi = bool(re_search_term(doc_text_lower, ["competing interest", "conflict of interest", "conflicts of interest", "competing financial interests"]))
                if not has_coi:
                    findings.append(Finding(
                        rule_id=rule.rule_code,
                        engine=EngineType.RAG_KNOWLEDGE,
                        category="compliance_formatting",
                        status=CheckStatus.FAIL,
                        severity=Severity.MAJOR,
                        title=f"Missing Competing Interests Declaration ({journal.name})",
                        expected_requirement=rule.requirement_description,
                        actual_observation="No 'Declaration of Competing Interests' section was located in the manuscript.",
                        guideline_source=GuidelineSource(
                            publisher=journal.publisher,
                            guideline_name=f"{journal.name} Submission Guidelines",
                            source_url=journal.official_url,
                            verified_on=str(verified_on),
                        ),
                        suggested_correction="Insert a 'Declaration of Competing Interest' statement before References.",
                        confidence=0.95,
                    ))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return EngineResult(
            engine=EngineType.RAG_KNOWLEDGE,
            execution_time_ms=round(elapsed_ms, 2),
            status="completed",
            findings=findings,
            summary={
                "journal_id": journal.id,
                "journal_name": journal.name,
                "guideline_version": guideline_version.version_tag,
                "total_guideline_checks": len(findings),
            },
        )


def re_search_term(text: str, terms: List[str]) -> bool:
    for t in terms:
        if t in text:
            return True
    return False

import re
from typing import List, Dict, Any, Set
from app.schemas.common import Finding, CheckStatus, Severity, EngineType, SourceLocation
from app.services.ingestion.extractor import ExtractedDocument


class CitationChecker:
    @staticmethod
    def verify(document: ExtractedDocument) -> List[Finding]:
        findings: List[Finding] = []

        # If document is scanned or has no text, cannot reliably verify
        if document.is_scanned or document.ocr_required:
            findings.append(Finding(
                rule_id="DETERM_CIT_UNABLE_TO_INSPECT",
                engine=EngineType.DETERMINISTIC,
                category="citation_reference",
                status=CheckStatus.UNABLE_TO_VERIFY,
                severity=Severity.CRITICAL,
                title="Citation Integrity Cannot Be Inspected on Scanned Manuscript",
                expected_requirement="Extractable text streams are required for cross-referencing citations and bibliography.",
                actual_observation=f"Document is scanned or low text density ({document.layout_metrics.get('ocr_diagnostic', 'OCR Required')}).",
                evidence=None,
                suggested_correction="Provide a digital PDF compiled from LaTeX/Word or perform OCR preprocessing before submission.",
                is_provisional=True,
                confidence=1.0,
            ))
            return findings

        if hasattr(document, "validation") and document.validation and not document.validation.is_plausible_manuscript:
            findings.append(Finding(
                rule_id="DETERM_CIT_UNABLE_TO_INSPECT_NON_MANUSCRIPT",
                engine=EngineType.DETERMINISTIC,
                category="citation_reference",
                status=CheckStatus.UNABLE_TO_VERIFY,
                severity=Severity.MAJOR,
                title="Citation Inspection Suspended (Non-Journal Manuscript Detected)",
                expected_requirement="Document must be a research manuscript to verify in-text citations against journal bibliography guidelines.",
                actual_observation=document.validation.warning_message or "Uploaded file does not appear to be a research manuscript prepared for journal review.",
                is_provisional=True,
                suggested_correction="Upload a research manuscript formatted for journal submission with in-text citations and a bibliography.",
                confidence=document.validation.confidence,
            ))
            return findings

        citations = document.citations
        references = document.references

        # Check if references section exists
        if not references:
            findings.append(Finding(
                rule_id="DETERM_REF_MISSING_SECTION",
                engine=EngineType.DETERMINISTIC,
                category="citation_reference",
                status=CheckStatus.FAIL,
                severity=Severity.CRITICAL,
                title="Missing References / Bibliography Section",
                expected_requirement="Manuscripts must contain a formal References or Bibliography section.",
                actual_observation="No References section or reference entries were detected in the manuscript.",
                evidence=None,
                suggested_correction="Include a numbered or alphabetized References section at the end of the manuscript.",
                confidence=1.0,
            ))
            return findings

        # 1. Cross-matching citations to references
        ref_indices: Set[int] = {r["index"] for r in references if "index" in r}
        cited_indices: Set[int] = set()

        missing_citations_findings = []
        for cit in citations:
            if cit.get("type") == "numeric" and "index" in cit:
                idx = cit["index"]
                cited_indices.add(idx)
                if idx not in ref_indices:
                    loc = SourceLocation(
                        page_number=cit.get("page_number"),
                        snippet=cit.get("snippet"),
                    )
                    missing_citations_findings.append((idx, loc))

        if missing_citations_findings:
            # Deduplicate by index
            missing_by_idx: Dict[int, SourceLocation] = {}
            for idx, loc in missing_citations_findings:
                if idx not in missing_by_idx:
                    missing_by_idx[idx] = loc

            for idx, loc in list(missing_by_idx.items())[:5]:  # report top 5 directly
                findings.append(Finding(
                    rule_id=f"DETERM_CIT_MISSING_REF_{idx}",
                    engine=EngineType.DETERMINISTIC,
                    category="citation_reference",
                    status=CheckStatus.FAIL,
                    severity=Severity.CRITICAL,
                    title=f"In-Text Citation [{idx}] Has No Matching Bibliography Entry",
                    expected_requirement=f"Every in-text citation [{idx}] must correspond to an entry in the References list.",
                    actual_observation=f"Citation [{idx}] appears in text on page {loc.page_number}, but reference #{idx} does not exist in the bibliography.",
                    evidence=loc.snippet,
                    source_location=loc,
                    suggested_correction=f"Add reference #{idx} to the bibliography or update the in-text citation tag.",
                    confidence=1.0,
                ))

        # 2. Check uncited bibliography entries
        uncited_refs = [r for r in references if r["index"] not in cited_indices]
        if uncited_refs and cited_indices:  # Only if numeric citing was actually used in the document
            for r in uncited_refs[:5]:
                findings.append(Finding(
                    rule_id=f"DETERM_REF_UNCITED_{r['index']}",
                    engine=EngineType.DETERMINISTIC,
                    category="citation_reference",
                    status=CheckStatus.WARNING,
                    severity=Severity.MODERATE,
                    title=f"Uncited Reference Entry #{r['index']}",
                    expected_requirement="All listed bibliography entries should be cited at least once within the manuscript text.",
                    actual_observation=f"Reference [{r['index']}] is listed in the bibliography but never cited in the body.",
                    evidence=r["raw_text"][:200],
                    suggested_correction=f"Cite reference [{r['index']}] where relevant in the manuscript or remove it from the bibliography.",
                    confidence=0.95,
                ))

        # 3. Check duplicate references
        seen_dois: Dict[str, int] = {}
        seen_texts: Dict[str, int] = {}
        for r in references:
            doi = r.get("detected_doi")
            idx = r["index"]
            if doi:
                if doi in seen_dois:
                    findings.append(Finding(
                        rule_id=f"DETERM_REF_DUPLICATE_DOI_{idx}",
                        engine=EngineType.DETERMINISTIC,
                        category="citation_reference",
                        status=CheckStatus.FAIL,
                        severity=Severity.MAJOR,
                        title=f"Duplicate Reference Detected (DOI Match)",
                        expected_requirement="Each reference in the bibliography must be unique.",
                        actual_observation=f"Reference #{idx} shares DOI '{doi}' with reference #{seen_dois[doi]}.",
                        evidence=r["raw_text"][:200],
                        suggested_correction=f"Merge reference #{idx} with reference #{seen_dois[doi]} and update citation keys.",
                        confidence=1.0,
                    ))
                else:
                    seen_dois[doi] = idx

            # Clean raw text match (first 60 chars)
            clean_snippet = re.sub(r"[^a-zA-Z0-9]+", "", r["raw_text"].lower())[:60]
            if len(clean_snippet) > 25:
                if clean_snippet in seen_texts:
                    orig_idx = seen_texts[clean_snippet]
                    if orig_idx != idx and not doi:  # avoid double reporting if already reported by doi
                        findings.append(Finding(
                            rule_id=f"DETERM_REF_DUPLICATE_TEXT_{idx}",
                            engine=EngineType.DETERMINISTIC,
                            category="citation_reference",
                            status=CheckStatus.WARNING,
                            severity=Severity.MODERATE,
                            title=f"Probable Duplicate Reference #{idx}",
                            expected_requirement="Each reference entry should be distinct.",
                            actual_observation=f"Reference #{idx} appears virtually identical to reference #{orig_idx}.",
                            evidence=r["raw_text"][:200],
                            suggested_correction=f"Consolidate reference #{idx} and reference #{orig_idx}.",
                            confidence=0.9,
                        ))
                else:
                    seen_texts[clean_snippet] = idx

        # 4. Check malformed reference entries
        for r in references:
            if r.get("is_malformed"):
                findings.append(Finding(
                    rule_id=f"DETERM_REF_MALFORMED_{r['index']}",
                    engine=EngineType.DETERMINISTIC,
                    category="citation_reference",
                    status=CheckStatus.WARNING,
                    severity=Severity.MINOR,
                    title=f"Malformed Reference Entry #{r['index']}",
                    expected_requirement="Reference entries should include author names, publication year, title, and venue or DOI.",
                    actual_observation="Reference entry is unusually short or missing key bibliographic fields (authors, publication year, title).",
                    evidence=r["raw_text"][:200],
                    suggested_correction="Verify and expand bibliographic details (authors, year, title, journal/conference, DOI).",
                    confidence=0.85,
                ))

        # 5. If everything passed cleanly, emit positive pass finding
        if not missing_citations_findings and not uncited_refs:
            findings.append(Finding(
                rule_id="DETERM_CIT_PERFECT_MATCH",
                engine=EngineType.DETERMINISTIC,
                category="citation_reference",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                title="Citation and Reference Consistency Verified",
                expected_requirement="Complete 1-to-1 correspondence between in-text citations and bibliography.",
                actual_observation=f"All {len(citations)} in-text citations match existing entries among the {len(references)} bibliography references.",
                evidence=f"{len(citations)} citations inspected across {len(references)} references.",
                confidence=1.0,
            ))

        return findings

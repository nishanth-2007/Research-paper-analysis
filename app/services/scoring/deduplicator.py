import re
import uuid
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.schemas.common import Finding, CheckStatus, Severity, SourceLocation, GuidelineSource


class IssueTier(str, Enum):
    SUBMISSION_BLOCKER = "submission_blocker"
    IMPROVEMENT_RECOMMENDED = "improvement_recommended"
    CHECK_OR_LIMITATION = "check_or_limitation"


class MeasuredValues(BaseModel):
    metric_name: Optional[str] = None
    detected_value: Optional[Any] = None
    allowed_value: Optional[Any] = None
    difference: Optional[Any] = None
    unit: Optional[str] = None


class EvidenceItem(BaseModel):
    engine: str
    rule_id: str
    finding_id: str
    source_location: Optional[SourceLocation] = None
    excerpt: Optional[str] = None
    guideline_source: Optional[GuidelineSource] = None
    actual_observation: str
    expected_requirement: str
    confidence: float = 1.0


class ConsolidatedIssue(BaseModel):
    issue_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    tier: IssueTier
    category: str  # journal_compliance, academic_quality, verification_status
    severity: str
    status: str = "open"  # open, in_progress, resolved, dismissed, unable_to_verify
    problem_statement: str
    why_it_matters: str
    actual_observation: str
    expected_requirement: Optional[str] = None
    measured_values: Optional[MeasuredValues] = None
    source_location: Optional[SourceLocation] = None
    recommended_action: str
    suggested_revision_guidance: Optional[str] = None
    verification_methods: List[str] = Field(default_factory=list)
    primary_engine: str
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    original_finding_ids: List[str] = Field(default_factory=list)
    technical_rule_ids: List[str] = Field(default_factory=list)
    guideline_source: Optional[GuidelineSource] = None
    verification_conflict: bool = False
    conflict_notes: Optional[str] = None
    confidence: float = 1.0


class VerificationCoverage(BaseModel):
    total_checks: int
    passed_count: int
    failed_count: int
    warning_count: int
    unverified_count: int
    coverage_percent: float
    summary_text: str


class IssueDeduplicator:
    """
    Intelligent issue-deduplication and consolidation layer.
    Consolidates raw findings from Deterministic, RAG, and LLM engines
    into deduplicated, researcher-actionable issues sorted by practical impact.
    """

    TAXONOMY_RULES = {
        "references": {
            "patterns": [r"DETERM_REF_MISSING", r"RAG_.*CITATION_STYLE"],
            "title": "Missing References / Bibliography Section",
            "tier": IssueTier.SUBMISSION_BLOCKER,
            "category": "journal_compliance",
            "severity": "critical",
            "why_it_matters": "Major journals require a complete, accurately formatted bibliography. Submissions without references are rejected at initial technical screening.",
            "recommended_action": "Add a dedicated References section at the conclusion of the manuscript containing full bibliographic citations.",
        },
        "abstract_length": {
            "patterns": [r"DETERM_ABS_WORD_COUNT", r"RAG_.*ABSTRACT_LIMIT"],
            "title": "Abstract Word Count Exceeds Guideline Limit",
            "tier": IssueTier.SUBMISSION_BLOCKER,
            "category": "journal_compliance",
            "severity": "major",
            "why_it_matters": "Publisher submission systems enforce hard word-limit caps on abstracts for indexing and metadata compliance.",
            "recommended_action": "Condense the abstract to within the required maximum word limit while retaining key contributions and findings.",
        },
        "missing_intro": {
            "patterns": [r"DETERM_SEC_MISSING_INTRODUCTION"],
            "title": "Missing Required Section: Introduction",
            "tier": IssueTier.SUBMISSION_BLOCKER,
            "category": "journal_compliance",
            "severity": "critical",
            "why_it_matters": "The Introduction establishes research context, motivates the problem statement, and outlines paper structure.",
            "recommended_action": "Include a clearly demarcated 'Introduction' heading articulating background and motivation.",
        },
        "missing_methods": {
            "patterns": [r"DETERM_SEC_MISSING_METHODOLOGY"],
            "title": "Missing Required Section: Methodology / Methods",
            "tier": IssueTier.SUBMISSION_BLOCKER,
            "category": "journal_compliance",
            "severity": "critical",
            "why_it_matters": "Academic peer reviewers require explicit methodology to evaluate scientific validity and ensure reproducibility.",
            "recommended_action": "Add an explicit 'Methodology' or 'Methods' section documenting experimental or mathematical formulations.",
        },
        "missing_results": {
            "patterns": [r"DETERM_SEC_MISSING_RESULTS"],
            "title": "Missing Required Section: Results / Evaluation",
            "tier": IssueTier.SUBMISSION_BLOCKER,
            "category": "journal_compliance",
            "severity": "critical",
            "why_it_matters": "Substantiating claims with empirical evidence or evaluation is a core requirement of peer-reviewed research.",
            "recommended_action": "Include a dedicated 'Results' or 'Experimental Evaluation' section with quantitative benchmarks.",
        },
        "missing_conclusion": {
            "patterns": [r"DETERM_SEC_MISSING_CONCLUSION"],
            "title": "Missing Required Section: Conclusion",
            "tier": IssueTier.IMPROVEMENT_RECOMMENDED,
            "category": "journal_compliance",
            "severity": "major",
            "why_it_matters": "Conclusions synthesize findings, discuss broader impact, and summarize principal contributions for readers.",
            "recommended_action": "Add a dedicated 'Conclusion' section summarizing outcomes and future research trajectories.",
        },
        "data_availability": {
            "patterns": [r"RAG_.*DATA_AVAILABILITY"],
            "title": "Missing Mandatory Statement: Data & Code Availability",
            "tier": IssueTier.IMPROVEMENT_RECOMMENDED,
            "category": "journal_compliance",
            "severity": "moderate",
            "why_it_matters": "Publisher transparency guidelines require clear statements explaining where datasets and source code can be accessed.",
            "recommended_action": "Add a 'Data Availability Statement' prior to references specifying data repositories or accession terms.",
        },
    }

    @classmethod
    def consolidate_findings(cls, findings: List[Finding]) -> List[ConsolidatedIssue]:
        # Only non-pass findings form actionable issues
        actionable = [f for f in findings if f.status in (CheckStatus.FAIL, CheckStatus.WARNING, CheckStatus.UNABLE_TO_VERIFY)]

        grouped: Dict[str, List[Finding]] = {}
        standalone: List[Finding] = []

        for f in actionable:
            matched_tax = None
            for key, meta in cls.TAXONOMY_RULES.items():
                if any(re.search(pat, f.rule_id, re.IGNORECASE) for pat in meta["patterns"]):
                    matched_tax = key
                    break

            if matched_tax:
                grouped.setdefault(matched_tax, []).append(f)
            else:
                standalone.append(f)

        consolidated: List[ConsolidatedIssue] = []

        # 1. Process grouped findings (taxonomically deduplicated)
        for tax_key, group in grouped.items():
            meta = cls.TAXONOMY_RULES[tax_key]
            primary = group[0]

            # Merge evidence items
            evidence_items = []
            orig_ids = []
            rule_ids = []
            verification_methods = []
            guideline_source = None

            for gf in group:
                orig_ids.append(gf.finding_id)
                rule_ids.append(gf.rule_id)
                v_method = "Deterministic Check" if gf.engine.value == "deterministic" else ("Publisher Guideline RAG" if gf.engine.value == "rag_knowledge" else "LLM Academic Review")
                if v_method not in verification_methods:
                    verification_methods.append(v_method)

                if gf.guideline_source:
                    guideline_source = gf.guideline_source

                has_excerpt = bool(gf.evidence and str(gf.evidence).strip())
                has_loc = bool(gf.source_location and (gf.source_location.section_name or gf.source_location.page_number))
                has_link = bool(gf.guideline_source and gf.guideline_source.source_url)

                if has_excerpt or has_loc or has_link:
                    evidence_items.append(EvidenceItem(
                        engine=gf.engine.value,
                        rule_id=gf.rule_id,
                        finding_id=gf.finding_id,
                        source_location=gf.source_location,
                        excerpt=gf.evidence,
                        guideline_source=gf.guideline_source,
                        actual_observation=gf.actual_observation,
                        expected_requirement=gf.expected_requirement,
                        confidence=gf.confidence,
                    ))

            # Detect measured values (e.g. abstract words)
            measured = None
            word_match = re.search(r"(\d+)\s+words\s+\((\d+)\s+words over limit\)", primary.actual_observation)
            if word_match:
                measured = MeasuredValues(
                    metric_name="Abstract Word Count",
                    detected_value=int(word_match.group(1)),
                    allowed_value=int(word_match.group(1)) - int(word_match.group(2)),
                    difference=int(word_match.group(2)),
                    unit="words",
                )

            # Detect verification conflicts
            conflict = False
            conflict_notes = None
            if len(group) > 1:
                # E.g., if one engine failed and another was unable_to_verify
                statuses = {g.status for g in group}
                if len(statuses) > 1:
                    conflict = True
                    conflict_notes = f"Engines reported varying statuses across this check: {[s.value for s in statuses]}."

            issue = ConsolidatedIssue(
                title=meta["title"],
                tier=meta["tier"],
                category=meta["category"],
                severity=meta["severity"],
                problem_statement=primary.title,
                why_it_matters=meta["why_it_matters"],
                actual_observation=primary.actual_observation,
                expected_requirement=primary.expected_requirement,
                measured_values=measured,
                source_location=primary.source_location,
                recommended_action=primary.suggested_correction or meta["recommended_action"],
                suggested_revision_guidance=cls._generate_revision_guidance(meta["title"]),
                verification_methods=verification_methods,
                primary_engine=primary.engine.value,
                evidence_items=evidence_items,
                original_finding_ids=orig_ids,
                technical_rule_ids=list(set(rule_ids)),
                guideline_source=guideline_source,
                verification_conflict=conflict,
                conflict_notes=conflict_notes,
                confidence=min(g.confidence for g in group),
            )
            consolidated.append(issue)

        # 2. Process standalone findings
        for sf in standalone:
            tier = IssueTier.IMPROVEMENT_RECOMMENDED
            if sf.status == CheckStatus.UNABLE_TO_VERIFY or sf.is_provisional:
                tier = IssueTier.CHECK_OR_LIMITATION
            elif sf.severity == Severity.CRITICAL and sf.status == CheckStatus.FAIL:
                tier = IssueTier.SUBMISSION_BLOCKER
            elif sf.severity in (Severity.MAJOR, Severity.MODERATE):
                tier = IssueTier.IMPROVEMENT_RECOMMENDED

            v_method = "Deterministic Check" if sf.engine.value == "deterministic" else ("Publisher Guideline RAG" if sf.engine.value == "rag_knowledge" else "LLM Academic Review")

            standalone_evidence: List[EvidenceItem] = []
            has_excerpt = bool(sf.evidence and str(sf.evidence).strip())
            has_loc = bool(sf.source_location and (sf.source_location.section_name or sf.source_location.page_number))
            has_link = bool(sf.guideline_source and sf.guideline_source.source_url)

            if has_excerpt or has_loc or has_link:
                standalone_evidence.append(EvidenceItem(
                    engine=sf.engine.value,
                    rule_id=sf.rule_id,
                    finding_id=sf.finding_id,
                    source_location=sf.source_location,
                    excerpt=sf.evidence,
                    guideline_source=sf.guideline_source,
                    actual_observation=sf.actual_observation,
                    expected_requirement=sf.expected_requirement,
                    confidence=sf.confidence,
                ))

            # Category mapping
            cat = "journal_compliance"
            if sf.engine.value == "llm_academic":
                cat = "journal_peer_review_rigor"
            elif sf.status == CheckStatus.UNABLE_TO_VERIFY:
                cat = "verification_status"

            issue = ConsolidatedIssue(
                title=sf.title,
                tier=tier,
                category=cat,
                severity=sf.severity.value,
                problem_statement=sf.actual_observation,
                why_it_matters=cls._infer_why_it_matters(sf),
                actual_observation=sf.actual_observation,
                expected_requirement=sf.expected_requirement,
                source_location=sf.source_location,
                recommended_action=sf.suggested_correction or sf.expected_requirement,
                suggested_revision_guidance=cls._generate_revision_guidance(sf.title),
                verification_methods=[v_method],
                primary_engine=sf.engine.value,
                evidence_items=standalone_evidence,
                original_finding_ids=[sf.finding_id],
                technical_rule_ids=[sf.rule_id],
                guideline_source=sf.guideline_source,
                confidence=sf.confidence,
            )
            consolidated.append(issue)

        # Sort consolidated issues: Submission Blockers -> Improvements -> Checks & Limitations
        tier_order = {
            IssueTier.SUBMISSION_BLOCKER: 0,
            IssueTier.IMPROVEMENT_RECOMMENDED: 1,
            IssueTier.CHECK_OR_LIMITATION: 2,
        }
        severity_order = {"critical": 0, "major": 1, "moderate": 2, "minor": 3, "info": 4}

        consolidated.sort(key=lambda x: (tier_order.get(x.tier, 3), severity_order.get(x.severity, 3), x.title))

        return consolidated

    @classmethod
    def calculate_coverage(cls, all_findings: List[Finding]) -> VerificationCoverage:
        total = len(all_findings)
        passed = sum(1 for f in all_findings if f.status == CheckStatus.PASS)
        failed = sum(1 for f in all_findings if f.status == CheckStatus.FAIL)
        warnings = sum(1 for f in all_findings if f.status == CheckStatus.WARNING)
        unverified = sum(1 for f in all_findings if f.status == CheckStatus.UNABLE_TO_VERIFY)

        coverage_pct = round(((total - unverified) / total * 100.0), 1) if total > 0 else 0.0

        summary_text = (
            f"{total - unverified} of {total} verification rules successfully executed ({coverage_pct}% coverage). "
            f"{passed} checks satisfied, {failed} requirements failed, {warnings} advisory warnings."
        )

        return VerificationCoverage(
            total_checks=total,
            passed_count=passed,
            failed_count=failed,
            warning_count=warnings,
            unverified_count=unverified,
            coverage_percent=coverage_pct,
            summary_text=summary_text,
        )

    @staticmethod
    def _infer_why_it_matters(finding: Finding) -> str:
        if finding.engine.value == "llm_academic":
            return "Rigorous scientific methodology and clear claims-evidence consistency significantly reduce journal peer-review revision cycles."
        if "citation" in finding.category or "ref" in finding.rule_id.lower():
            return "Accurate citation trails allow reviewers and readers to verify prior art and foundational algorithms."
        if "layout" in finding.rule_id.lower() or "page" in finding.rule_id.lower():
            return "Adherence to page budgets and typographical constraints is strictly verified during camera-ready production."
        return "Conformity to verified publisher specifications ensures smooth editorial workflow and avoids desk rejection."

    @staticmethod
    def _generate_revision_guidance(title: str) -> str:
        t_low = title.lower()
        if "abstract" in t_low and "word" in t_low:
            return "Drafting Tip: Remove conversational filler phrases ('In this paper we propose', 'It is widely known that'). Focus strictly on (1) Problem, (2) Proposed Approach, (3) Key Metric Result."
        if "introduction" in t_low:
            return "Drafting Tip: Open with the broad motivation, narrow down to the specific challenge, clearly state limitations of existing art, and summarize key contributions in bullet points."
        if "methodology" in t_low:
            return "Drafting Tip: Provide a clear architectural flowchart or equation block, define notation tables, and state parameter values explicitly for reproducible experiments."
        if "research question" in t_low:
            return "Drafting Tip: Explicitly formulate questions e.g., 'RQ1: How does model X perform compared to standard baseline Y on dataset Z under resource-constrained settings?'"
        if "limitation" in t_low or "threat" in t_low:
            return "Drafting Tip: Add a paragraph acknowledging constraints (dataset diversity, hardware assumptions, edge cases) and threats to construct, internal, and external validity."
        return "Drafting Tip: Ensure clear, evidence-supported language aligning with target journal submission standards."

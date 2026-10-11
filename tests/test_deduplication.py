import pytest
from app.schemas.common import Finding, CheckStatus, Severity, EngineType, GuidelineSource
from app.services.scoring.deduplicator import IssueDeduplicator, IssueTier


def test_issue_deduplication_references():
    findings = [
        Finding(
            rule_id="DETERM_REF_MISSING_SECTION",
            engine=EngineType.DETERMINISTIC,
            category="citation_reference",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            title="Missing References / Bibliography Section",
            expected_requirement="Manuscripts must contain a formal References or Bibliography section.",
            actual_observation="No References section or reference entries were detected in the manuscript.",
        ),
        Finding(
            rule_id="RAG_IEEE_CITATION_STYLE",
            engine=EngineType.RAG_KNOWLEDGE,
            category="citation_reference",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            title="Missing Citation List per IEEE Guidelines",
            expected_requirement="IEEE requires numbered references list [1], [2].",
            actual_observation="References list is absent, violating IEEE citation policy.",
            guideline_source=GuidelineSource(publisher="IEEE", source_url="https://ieeeaccess.ieee.org"),
        ),
    ]

    consolidated = IssueDeduplicator.consolidate_findings(findings)

    # Both findings should be consolidated into a single issue
    assert len(consolidated) == 1
    issue = consolidated[0]
    assert issue.tier == IssueTier.SUBMISSION_BLOCKER
    assert issue.title == "Missing References / Bibliography Section"
    assert len(issue.original_finding_ids) == 2
    assert "Deterministic Check" in issue.verification_methods
    assert "Publisher Guideline RAG" in issue.verification_methods
    assert issue.guideline_source is not None


def test_verification_coverage_calculation():
    findings = [
        Finding(
            rule_id="R1",
            engine=EngineType.DETERMINISTIC,
            category="manuscript_completeness",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            title="Intro Passed",
            expected_requirement="Req",
            actual_observation="Passed",
        ),
        Finding(
            rule_id="R2",
            engine=EngineType.DETERMINISTIC,
            category="manuscript_completeness",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            title="Methods Failed",
            expected_requirement="Req",
            actual_observation="Failed",
        ),
        Finding(
            rule_id="R3",
            engine=EngineType.DETERMINISTIC,
            category="compliance_formatting",
            status=CheckStatus.WARNING,
            severity=Severity.MODERATE,
            title="Short Section",
            expected_requirement="Req",
            actual_observation="Warn",
        ),
        Finding(
            rule_id="R4",
            engine=EngineType.DETERMINISTIC,
            category="compliance_formatting",
            status=CheckStatus.UNABLE_TO_VERIFY,
            severity=Severity.MAJOR,
            title="Scanned Page",
            expected_requirement="Req",
            actual_observation="Unverified",
        ),
    ]

    coverage = IssueDeduplicator.calculate_coverage(findings)

    assert coverage.total_checks == 4
    assert coverage.passed_count == 1
    assert coverage.failed_count == 1
    assert coverage.warning_count == 1
    assert coverage.unverified_count == 1
    assert coverage.coverage_percent == 75.0

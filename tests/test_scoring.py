from app.services.scoring.engine import ReadinessScoringEngine
from app.schemas.common import Finding, CheckStatus, Severity, EngineType


def test_deterministic_scoring_consistency():
    findings = [
        Finding(
            rule_id="RULE_PASS_1",
            engine=EngineType.DETERMINISTIC,
            category="citation_reference",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            title="Clean citation",
            expected_requirement="Req",
            actual_observation="Obs",
        ),
        Finding(
            rule_id="RULE_FAIL_1",
            engine=EngineType.DETERMINISTIC,
            category="compliance_formatting",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            title="Critical Layout Failure",
            expected_requirement="Max 10 pages",
            actual_observation="Paper has 20 pages",
        ),
    ]

    score1 = ReadinessScoringEngine.calculate_readiness_score(findings)
    score2 = ReadinessScoringEngine.calculate_readiness_score(findings)

    assert score1.overall_score == score2.overall_score
    assert score1.critical_issues_count == 1
    assert score1.category_scores["compliance_formatting"].score < 100.0


def test_provisional_scoring_flag():
    unverified_findings = [
        Finding(
            rule_id="RULE_UNVERIFIED",
            engine=EngineType.DETERMINISTIC,
            category="compliance_formatting",
            status=CheckStatus.UNABLE_TO_VERIFY,
            severity=Severity.MAJOR,
            title="Scanned page cannot be verified",
            expected_requirement="Digital text required",
            actual_observation="Scanned PDF artifact",
            is_provisional=True,
        )
    ]

    score = ReadinessScoringEngine.calculate_readiness_score(unverified_findings)
    assert score.is_provisional is True
    assert score.unverified_count == 1
    assert score.category_scores["compliance_formatting"].is_provisional is True


def test_recommendation_ranking():
    findings = [
        Finding(
            rule_id="RULE_MINOR",
            engine=EngineType.DETERMINISTIC,
            category="compliance_formatting",
            status=CheckStatus.WARNING,
            severity=Severity.MINOR,
            title="Minor issue",
            expected_requirement="R",
            actual_observation="O",
        ),
        Finding(
            rule_id="RULE_CRITICAL",
            engine=EngineType.DETERMINISTIC,
            category="citation_reference",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            title="Missing citation",
            expected_requirement="R",
            actual_observation="O",
        ),
    ]

    recs = ReadinessScoringEngine.rank_actionable_recommendations(findings)
    assert len(recs) == 2
    # Critical issue must be ranked #1
    assert recs[0].rule_id == "RULE_CRITICAL"
    assert recs[0].priority_rank == 1
    assert recs[1].rule_id == "RULE_MINOR"
    assert recs[1].priority_rank == 2

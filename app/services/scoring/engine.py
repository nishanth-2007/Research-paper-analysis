from typing import List, Dict, Any, Optional
from app.schemas.common import Finding, CheckStatus, Severity
from app.schemas.scoring import (
    ReadinessScoreResponse,
    CategoryScoreDetail,
    DeductionDetail,
    ScoreCalculationBreakdown,
    EngineScoreDetail,
    SectionScoreDetail,
)
from app.schemas.report import ActionableRecommendation
from app.services.scoring.config import (
    DEFAULT_CATEGORY_WEIGHTS,
    SEVERITY_DEDUCTION_TABLE,
    UNVERIFIED_CHECK_PENALTY,
)


class ReadinessScoringEngine:
    @classmethod
    def calculate_readiness_score(
        cls,
        findings: List[Finding],
        category_weights_override: Optional[Dict[str, Any]] = None,
    ) -> ReadinessScoreResponse:
        weights_config = category_weights_override or DEFAULT_CATEGORY_WEIGHTS

        # Initialize category details
        categories: Dict[str, CategoryScoreDetail] = {}
        for cat_id, meta in weights_config.items():
            categories[cat_id] = CategoryScoreDetail(
                category_id=cat_id,
                category_label=meta["label"],
                score=100.0,
                weight=meta["weight"],
                weighted_score=meta["weight"] * 100.0,
                passed_count=0,
                failed_count=0,
                warning_count=0,
                unverified_count=0,
                is_provisional=False,
                deductions=[],
            )

        is_overall_provisional = False
        provisional_reasons: List[str] = []

        critical_count = 0
        warning_count = 0
        unverified_count = 0

        # Process each finding
        for f in findings:
            cat_id = f.category
            if cat_id not in categories:
                # Fallback to closest category
                cat_id = "compliance_formatting"

            cat_item = categories[cat_id]

            if f.status == CheckStatus.PASS:
                cat_item.passed_count += 1

            elif f.status == CheckStatus.FAIL:
                cat_item.failed_count += 1
                if f.severity == Severity.CRITICAL:
                    critical_count += 1

                pts = SEVERITY_DEDUCTION_TABLE.get(f.severity.value, 15.0)
                cat_item.deductions.append(DeductionDetail(
                    rule_id=f.rule_id,
                    severity=f.severity.value,
                    points_deducted=pts,
                    reason=f.actual_observation[:120],
                ))

            elif f.status == CheckStatus.WARNING:
                cat_item.warning_count += 1
                warning_count += 1
                pts = SEVERITY_DEDUCTION_TABLE.get(f.severity.value, 10.0) * 0.75
                cat_item.deductions.append(DeductionDetail(
                    rule_id=f.rule_id,
                    severity=f.severity.value,
                    points_deducted=round(pts, 1),
                    reason=f.actual_observation[:120],
                ))

            elif f.status == CheckStatus.UNABLE_TO_VERIFY:
                cat_item.unverified_count += 1
                unverified_count += 1
                cat_item.is_provisional = True
                is_overall_provisional = True
                provisional_reasons.append(f"{f.title}: {f.actual_observation[:100]}")

                # Do not treat as pass: apply provisional deduction
                cat_item.deductions.append(DeductionDetail(
                    rule_id=f.rule_id,
                    severity="provisional_unverified",
                    points_deducted=UNVERIFIED_CHECK_PENALTY,
                    reason=f"Check could not be completed reliably: {f.actual_observation[:100]}",
                ))

        # Calculate category scores
        total_weighted_sum = 0.0
        total_weight = 0.0

        for cat_id, cat_item in categories.items():
            total_deductions = sum(d.points_deducted for d in cat_item.deductions)
            calculated_score = max(0.0, 100.0 - total_deductions)
            cat_item.score = round(calculated_score, 1)
            cat_item.weighted_score = round(calculated_score * cat_item.weight, 2)
            total_weighted_sum += cat_item.weighted_score
            total_weight += cat_item.weight

        overall_score = round(total_weighted_sum / total_weight, 1) if total_weight > 0 else 0.0
        overall_score = max(0.0, min(100.0, overall_score))

        # Calculate Individual Engine Scores
        engine_configs = {
            "deterministic": "Deterministic Verification Engine",
            "rag_knowledge": "Journal Guidelines RAG Engine",
            "llm_academic": "LLM Research Evaluation Engine",
        }
        engine_scores: Dict[str, EngineScoreDetail] = {}
        for eng_key, eng_name in engine_configs.items():
            eng_findings = [f for f in findings if f.engine.value == eng_key]
            p_cnt = sum(1 for f in eng_findings if f.status == CheckStatus.PASS)
            f_cnt = sum(1 for f in eng_findings if f.status == CheckStatus.FAIL)
            w_cnt = sum(1 for f in eng_findings if f.status == CheckStatus.WARNING)
            u_cnt = sum(1 for f in eng_findings if f.status == CheckStatus.UNABLE_TO_VERIFY)
            is_prov = any(f.is_provisional or f.status == CheckStatus.UNABLE_TO_VERIFY for f in eng_findings)

            eng_deductions = 0.0
            for f in eng_findings:
                if f.status == CheckStatus.FAIL:
                    eng_deductions += SEVERITY_DEDUCTION_TABLE.get(f.severity.value, 15.0)
                elif f.status == CheckStatus.WARNING:
                    eng_deductions += SEVERITY_DEDUCTION_TABLE.get(f.severity.value, 10.0) * 0.5
                elif f.status == CheckStatus.UNABLE_TO_VERIFY:
                    eng_deductions += UNVERIFIED_CHECK_PENALTY

            e_score = max(0.0, min(100.0, round(100.0 - eng_deductions, 1)))
            engine_scores[eng_key] = EngineScoreDetail(
                engine_id=eng_key,
                engine_name=eng_name,
                score=e_score,
                passed_count=p_cnt,
                failed_count=f_cnt,
                warning_count=w_cnt,
                unverified_count=u_cnt,
                is_provisional=is_prov,
                weight=0.33,
            )

        # Calculate Manuscript Section Scores
        section_configs = {
            "abstract": ("Abstract", [r"abstract", r"abs_word"]),
            "introduction": ("Introduction", [r"introduction", r"research_question"]),
            "methodology": ("Methodology", [r"method", r"methodology"]),
            "results": ("Results / Evaluation", [r"result", r"evaluation", r"figure", r"table", r"claim"]),
            "conclusion": ("Conclusion", [r"conclusion", r"limitation", r"validity"]),
            "references": ("References / Bibliography", [r"ref", r"citation", r"biblio"]),
        }
        section_scores: Dict[str, SectionScoreDetail] = {}

        for sec_key, (sec_name, sec_patterns) in section_configs.items():
            import re
            sec_findings = []
            for f in findings:
                loc_sec = (f.source_location.section_name or "").lower() if f.source_location else ""
                rule_match = any(re.search(p, f.rule_id, re.IGNORECASE) for p in sec_patterns)
                title_match = any(re.search(p, f.title, re.IGNORECASE) for p in sec_patterns)
                loc_match = any(re.search(p, loc_sec, re.IGNORECASE) for p in sec_patterns)
                if rule_match or title_match or loc_match:
                    sec_findings.append(f)

            sec_pass = sum(1 for f in sec_findings if f.status == CheckStatus.PASS)
            sec_fail = sum(1 for f in sec_findings if f.status == CheckStatus.FAIL)
            sec_warn = sum(1 for f in sec_findings if f.status == CheckStatus.WARNING)
            sec_unver = sum(1 for f in sec_findings if f.status == CheckStatus.UNABLE_TO_VERIFY)

            has_evidence = len(sec_findings) > 0 and (sec_pass > 0 or sec_fail > 0 or sec_warn > 0)
            if sec_unver > 0 and not (sec_pass or sec_fail):
                status_str = "unverified"
                evidence_notes = "Insufficient or unextractable text to verify this section reliably."
                sec_score = 75.0
            elif sec_fail > 0:
                status_str = "needs_revision"
                evidence_notes = f"{sec_fail} requirement violation(s) identified."
                deduct = sum(SEVERITY_DEDUCTION_TABLE.get(f.severity.value, 15.0) for f in sec_findings if f.status == CheckStatus.FAIL)
                sec_score = max(0.0, min(100.0, round(100.0 - deduct, 1)))
            elif sec_warn > 0:
                status_str = "needs_revision"
                evidence_notes = f"{sec_warn} advisory suggestion(s) to improve quality."
                sec_score = 85.0
            else:
                status_str = "pass"
                evidence_notes = "Section satisfies guideline standards."
                sec_score = 100.0

            section_scores[sec_key] = SectionScoreDetail(
                section_id=sec_key,
                section_name=sec_name,
                score=sec_score,
                status=status_str,
                passed_count=sec_pass,
                failed_count=sec_fail,
                warning_count=sec_warn,
                has_sufficient_evidence=has_evidence,
                evidence_notes=evidence_notes,
            )

        # Assign readiness tier
        if overall_score >= 85.0 and critical_count == 0:
            tier = "Ready for Submission (High Confidence)"
        elif overall_score >= 70.0 and critical_count == 0:
            tier = "Minor Revisions Required"
        elif overall_score >= 50.0:
            tier = "Substantial Revisions Required"
        else:
            tier = "Early Draft / Critical Deficiencies"

        breakdown = ScoreCalculationBreakdown(
            category_scores=categories,
            critical_penalty_applied=0.0,
            formula_explanation=(
                "Overall Score = Sum(Category_Score * Category_Weight). "
                "Each category starts at 100 with deterministic deductions: "
                "Critical (-30), Major (-18), Moderate (-10), Minor (-4), Unverified (-12). "
                "Provisional score applied when structural elements cannot be verified."
            ),
        )

        return ReadinessScoreResponse(
            overall_score=overall_score,
            readiness_tier=tier,
            is_provisional=is_overall_provisional,
            provisional_reason="; ".join(provisional_reasons[:2]) if provisional_reasons else None,
            category_scores=categories,
            engine_scores=engine_scores,
            section_scores=section_scores,
            critical_issues_count=critical_count,
            warnings_count=warning_count,
            unverified_count=unverified_count,
            breakdown=breakdown,
        )

    @classmethod
    def rank_actionable_recommendations(cls, findings: List[Finding]) -> List[ActionableRecommendation]:
        """
        Sorts non-passing findings by severity, priority impact, and category.
        """
        severity_rank = {
            Severity.CRITICAL: 1,
            Severity.MAJOR: 2,
            Severity.MODERATE: 3,
            Severity.MINOR: 4,
            Severity.INFO: 5,
        }

        actionable_findings = [
            f for f in findings
            if f.status in (CheckStatus.FAIL, CheckStatus.WARNING, CheckStatus.UNABLE_TO_VERIFY)
        ]

        actionable_findings.sort(
            key=lambda x: (severity_rank.get(x.severity, 5), x.rule_id)
        )

        recommendations: List[ActionableRecommendation] = []
        for rank, f in enumerate(actionable_findings, 1):
            impact = f"Fix to recover +{SEVERITY_DEDUCTION_TABLE.get(f.severity.value, 10.0):.0f} pts" if f.status == CheckStatus.FAIL else "Fix to recover +5 pts"
            recommendations.append(ActionableRecommendation(
                priority_rank=rank,
                rule_id=f.rule_id,
                category=f.category,
                severity=f.severity.value,
                title=f.title,
                action_item=f.suggested_correction or f.expected_requirement,
                estimated_impact=impact,
                source_location=f.source_location,
            ))

        return recommendations

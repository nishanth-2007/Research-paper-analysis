import io
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.schemas.report import CompleteAnalysisReport


class PDFReportExporter:
    @classmethod
    def generate_pdf_bytes(cls, report: CompleteAnalysisReport) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=8,
        )

        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=14,
            spaceAfter=6,
        )

        h3_style = ParagraphStyle(
            "ReportH3",
            parent=styles["Heading3"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=8,
            spaceAfter=4,
        )

        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#2D3748"),
        )

        story = []

        # Header / Title
        story.append(Paragraph("Journal Readiness & Manuscript Verification Report", title_style))
        story.append(Paragraph(f"<b>Manuscript:</b> {report.manuscript_title}", body_style))
        if report.target_journal_name:
            story.append(Paragraph(f"<b>Target Journal:</b> {report.target_journal_name} ({report.guideline_version_tag or 'Latest'})", body_style))
        story.append(Paragraph(f"<b>Date Generated:</b> {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}", body_style))
        story.append(Spacer(1, 12))

        # Readiness Score Box
        score_val = report.readiness_score.overall_score
        tier_val = report.readiness_score.readiness_tier
        score_color = colors.HexColor("#2F855A") if score_val >= 80 else (colors.HexColor("#DD6B20") if score_val >= 60 else colors.HexColor("#C53030"))

        score_data = [
            [
                Paragraph(f"<b>Overall Readiness Score:</b> <font color='{score_color.hexval()}'>{score_val:.1f} / 100</font>", h2_style),
                Paragraph(f"<b>Status:</b> {tier_val}", body_style),
            ]
        ]
        score_table = Table(score_data, colWidths=[300, 240])
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EDF2F7")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 12))

        # Executive Summary
        story.append(Paragraph("Executive Summary", h2_style))
        story.append(Paragraph(report.executive_summary.synthesis, body_style))
        story.append(Spacer(1, 10))

        # Category Breakdown Table
        story.append(Paragraph("Category Performance Breakdown", h2_style))
        cat_rows = [["Evaluation Category", "Weight", "Score", "Issues"]]
        for cat_id, cat_data in report.readiness_score.category_scores.items():
            issues = f"{cat_data.failed_count} fails, {cat_data.warning_count} warns"
            cat_rows.append([
                cat_data.category_label,
                f"{cat_data.weight * 100:.0f}%",
                f"{cat_data.score:.1f} / 100",
                issues,
            ])

        cat_table = Table(cat_rows, colWidths=[240, 70, 90, 140])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 12))

        # Prioritized Action Plan
        if report.consolidated_issues:
            story.append(Paragraph("Prioritized Action Plan for Authors", h2_style))
            blockers = [c for c in report.consolidated_issues if c.tier.value == "submission_blocker"]
            improvements = [c for c in report.consolidated_issues if c.tier.value == "improvement_recommended"]
            checks = [c for c in report.consolidated_issues if c.tier.value == "check_or_limitation"]

            if blockers:
                story.append(Paragraph("<b>[SUBMISSION BLOCKERS]</b>", h3_style))
                for b in blockers[:5]:
                    b_text = f"<b>• {b.title} ({b.severity.upper()})</b><br/>{b.why_it_matters}<br/><b>Action:</b> {b.recommended_action}"
                    story.append(Paragraph(b_text, body_style))
                    story.append(Spacer(1, 4))

            if improvements:
                story.append(Spacer(1, 6))
                story.append(Paragraph("<b>[RECOMMENDED IMPROVEMENTS]</b>", h3_style))
                for imp in improvements[:4]:
                    imp_text = f"<b>• {imp.title} ({imp.severity.upper()})</b><br/>{imp.why_it_matters}<br/><b>Action:</b> {imp.recommended_action}"
                    story.append(Paragraph(imp_text, body_style))
                    story.append(Spacer(1, 4))

            if checks:
                story.append(Spacer(1, 6))
                story.append(Paragraph("<b>[CHECKS & LIMITATIONS]</b>", h3_style))
                for chk in checks[:3]:
                    chk_text = f"<b>• {chk.title}</b>: {chk.actual_observation}"
                    story.append(Paragraph(chk_text, body_style))
                    story.append(Spacer(1, 4))

        elif report.actionable_recommendations:
            story.append(Paragraph("Priority Action Items for Authors", h2_style))
            for rec in report.actionable_recommendations[:6]:
                rec_text = f"<b>#{rec.priority_rank} [{rec.severity.upper()}] {rec.title}</b><br/>{rec.action_item}"
                story.append(Paragraph(rec_text, body_style))
                story.append(Spacer(1, 6))

        # Limitations / Disclaimer
        story.append(Spacer(1, 12))
        story.append(Paragraph("Verification Scope & Disclaimers", h2_style))
        disclaimer_p = Paragraph(
            f"<i>{report.readiness_score.disclaimer}</i>",
            body_style,
        )
        story.append(disclaimer_p)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

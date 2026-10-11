import io
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import inch


class ManuscriptDocumentExporter:
    @classmethod
    def generate_docx(cls, data: dict) -> bytes:
        """
        Generate an official Microsoft Word (.docx) manuscript formatted as per
        academic publisher conventions (IEEE, Nature, ACM, Elsevier, PLOS).
        """
        doc = Document()

        for section in doc.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

        # Title
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_after = Pt(8)
        r_title = p_title.add_run(data.get("title", "Manuscript Title"))
        r_title.bold = True
        r_title.font.name = "Times New Roman"
        r_title.font.size = Pt(18)
        r_title.font.color.rgb = RGBColor(15, 23, 42)

        # Authors
        authors = data.get("authors", [])
        if authors:
            p_auth = doc.add_paragraph()
            p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_auth.paragraph_format.space_after = Pt(2)
            auth_names = ", ".join([a.get("name", "") for a in authors if a.get("name")])
            r_auth = p_auth.add_run(auth_names)
            r_auth.bold = True
            r_auth.font.name = "Times New Roman"
            r_auth.font.size = Pt(11)

            # Affiliations
            affils = [a.get("affiliation", "") for a in authors if a.get("affiliation")]
            if affils:
                p_aff = doc.add_paragraph()
                p_aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_aff.paragraph_format.space_after = Pt(6)
                r_aff = p_aff.add_run(" | ".join(set(affils)))
                r_aff.italic = True
                r_aff.font.name = "Times New Roman"
                r_aff.font.size = Pt(9.5)
                r_aff.font.color.rgb = RGBColor(71, 85, 105)

        # Journal Venue Tagline
        journal_name = data.get("target_journal_name", "Academic Journal")
        p_j = doc.add_paragraph()
        p_j.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_j.paragraph_format.space_after = Pt(14)
        r_j = p_j.add_run(f"Formatted for Target Venue: {journal_name}")
        r_j.font.name = "Times New Roman"
        r_j.font.size = Pt(9)
        r_j.font.color.rgb = RGBColor(99, 102, 241)

        # Abstract
        abstract = data.get("abstract", "")
        if abstract:
            p_abs = doc.add_paragraph()
            p_abs.paragraph_format.space_after = Pt(6)
            p_abs.paragraph_format.line_spacing = 1.15
            r_abs_lbl = p_abs.add_run("Abstract— ")
            r_abs_lbl.bold = True
            r_abs_lbl.font.name = "Times New Roman"
            r_abs_lbl.font.size = Pt(10)
            r_abs_txt = p_abs.add_run(abstract)
            r_abs_txt.font.name = "Times New Roman"
            r_abs_txt.font.size = Pt(10)

        # Keywords / Index Terms
        keywords = data.get("keywords", [])
        if keywords:
            p_kw = doc.add_paragraph()
            p_kw.paragraph_format.space_after = Pt(16)
            r_kw_lbl = p_kw.add_run("Index Terms— ")
            r_kw_lbl.bold = True
            r_kw_lbl.italic = True
            r_kw_lbl.font.name = "Times New Roman"
            r_kw_lbl.font.size = Pt(10)
            r_kw_txt = p_kw.add_run(", ".join(keywords))
            r_kw_txt.font.name = "Times New Roman"
            r_kw_txt.font.size = Pt(10)

        # Sections
        sections = data.get("sections", [])
        for sec in sections:
            sec_num = sec.get("number", "")
            sec_title = sec.get("title", "")
            full_heading = f"{sec_num} {sec_title}".strip()

            h = doc.add_heading(full_heading, level=1)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            for r in h.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.bold = True
                r.font.color.rgb = RGBColor(15, 23, 42)

            content = sec.get("content", "")
            for para in content.split("\n\n"):
                clean_p = para.strip()
                if clean_p:
                    p = doc.add_paragraph()
                    p.paragraph_format.line_spacing = 1.15
                    p.paragraph_format.space_after = Pt(6)
                    r = p.add_run(clean_p)
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(10.5)

        # Declarations
        decls = data.get("declarations", {})
        if decls:
            h_dec = doc.add_heading("DECLARATIONS & STATEMENTS", level=1)
            h_dec.paragraph_format.space_before = Pt(16)
            h_dec.paragraph_format.space_after = Pt(6)
            for r in h_dec.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.bold = True

            for k, v in decls.items():
                if v:
                    label = re.sub(r'([A-Z])', r' \1', k).replace("_", " ").strip().title()
                    p = doc.add_paragraph()
                    p.paragraph_format.space_after = Pt(4)
                    r_lbl = p.add_run(f"{label}: ")
                    r_lbl.bold = True
                    r_lbl.font.name = "Times New Roman"
                    r_lbl.font.size = Pt(10)
                    r_val = p.add_run(v)
                    r_val.font.name = "Times New Roman"
                    r_val.font.size = Pt(10)

        # References
        refs = data.get("references", [])
        if refs:
            h_ref = doc.add_heading("REFERENCES", level=1)
            h_ref.paragraph_format.space_before = Pt(16)
            h_ref.paragraph_format.space_after = Pt(6)
            for r in h_ref.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.bold = True

            for ref in refs:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.left_indent = Inches(0.25)
                r = p.add_run(ref)
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def generate_pdf(cls, data: dict) -> bytes:
        """
        Generate an official PDF manuscript formatted for publication submission.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ManuscriptTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=1,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=8,
        )

        auth_style = ParagraphStyle(
            'ManuscriptAuthor',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            alignment=1,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=4,
        )

        venue_style = ParagraphStyle(
            'ManuscriptVenue',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            alignment=1,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=12,
        )

        heading_style = ParagraphStyle(
            'ManuscriptHeading',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=12,
            spaceAfter=4,
        )

        body_style = ParagraphStyle(
            'ManuscriptBody',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=6,
        )

        ref_style = ParagraphStyle(
            'ManuscriptRef',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#334155'),
            spaceAfter=3,
        )

        story = []

        # Title
        story.append(Paragraph(data.get("title", "Manuscript Title"), title_style))

        # Authors
        authors = data.get("authors", [])
        if authors:
            auth_names = ", ".join([a.get("name", "") for a in authors if a.get("name")])
            story.append(Paragraph(auth_names, auth_style))

        # Venue
        j_name = data.get("target_journal_name", "Academic Venue")
        story.append(Paragraph(f"Formatted for: {j_name}", venue_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=8))

        # Abstract
        abstract = data.get("abstract", "")
        if abstract:
            story.append(Paragraph(f"<b>Abstract—</b> {abstract}", body_style))
            story.append(Spacer(1, 4))

        # Keywords
        keywords = data.get("keywords", [])
        if keywords:
            story.append(Paragraph(f"<b><i>Index Terms—</i></b> {', '.join(keywords)}", body_style))
            story.append(Spacer(1, 8))

        # Sections
        for sec in data.get("sections", []):
            h_text = f"{sec.get('number', '')} {sec.get('title', '')}".strip()
            story.append(Paragraph(h_text, heading_style))

            content = sec.get("content", "")
            for para in content.split("\n\n"):
                cp = para.strip()
                if cp:
                    story.append(Paragraph(cp, body_style))

        # Declarations
        decls = data.get("declarations", {})
        if decls:
            story.append(Paragraph("DECLARATIONS & STATEMENTS", heading_style))
            for k, v in decls.items():
                if v:
                    label = re.sub(r'([A-Z])', r' \1', k).replace("_", " ").strip().title()
                    story.append(Paragraph(f"<b>{label}:</b> {v}", body_style))

        # References
        refs = data.get("references", [])
        if refs:
            story.append(Paragraph("REFERENCES", heading_style))
            for ref in refs:
                story.append(Paragraph(ref, ref_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

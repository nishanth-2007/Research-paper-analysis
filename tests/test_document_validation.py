import pytest
from app.services.ingestion.document_validator import DocumentPlausibilityValidator


def test_cv_detection():
    cv_text = """
    GODASU NISHANTH
    Email: godasunishanth04@gmail.com | Mobile: +91 7702842815
    linkedin.com/in/nishanth-godasu | github.com/nishanth-2007

    EDUCATION
    MVGR College of Engineering, Visakhapatnam, Andhra Pradesh
    B.Tech in Computer Science and Engineering | CGPA: 8.9

    TECHNICAL SKILLS
    Python, FastAPI, PyTorch, React, PostgreSQL, Docker, Git

    WORK EXPERIENCE
    Software Engineer Intern at TechCorp
    Developed microservices and automated CI/CD pipelines.

    PROJECTS
    ScholarCheck AI - Academic manuscript analyzer.
    """
    res = DocumentPlausibilityValidator.validate(
        raw_text=cv_text,
        page_count=1,
        word_count=150,
        is_scanned=False,
        sections=[{"title": "Preamble", "normalized_title": "preamble", "content": cv_text}],
    )

    assert res.is_plausible_manuscript is False
    assert res.document_type == "resume_or_cv"
    assert "Curriculum Vitae" in res.warning_message or "Résumé" in res.warning_message


def test_research_paper_plausibility():
    paper_text = """
    Evaluating Neural Graph Attention for Low-Resource Text Classification

    ABSTRACT
    We propose a novel graph attention architecture for few-shot NLP. 
    Our approach outperforms baseline transformers by 4.2% on standard benchmarks.

    1. INTRODUCTION
    Deep learning architectures have revolutionized natural language understanding...

    2. METHODOLOGY
    Let G = (V, E) be a directed semantic graph with node features X...

    3. EXPERIMENTAL RESULTS
    We evaluate our method on GLUE and SuperGLUE benchmarks...

    4. CONCLUSION
    In this work, we introduced a structured graph attention network...

    REFERENCES
    [1] Vaswani et al., Attention is all you need, NeurIPS 2017.
    """
    res = DocumentPlausibilityValidator.validate(
        raw_text=paper_text,
        page_count=8,
        word_count=2500,
        is_scanned=False,
        sections=[
            {"title": "Abstract", "normalized_title": "abstract", "content": "We propose..."},
            {"title": "Introduction", "normalized_title": "introduction", "content": "Deep learning..."},
            {"title": "Methodology", "normalized_title": "methodology", "content": "Let G..."},
            {"title": "References", "normalized_title": "references", "content": "[1] Vaswani..."},
        ],
    )

    assert res.is_plausible_manuscript is True
    assert res.document_type == "research_manuscript"
    assert res.warning_message is None

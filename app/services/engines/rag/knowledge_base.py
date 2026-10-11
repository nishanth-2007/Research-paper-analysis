from datetime import datetime, timezone
from typing import List, Dict, Any
from app.services.engines.rag.embeddings import EmbeddingProvider


DEFAULT_JOURNAL_SEEDS: List[Dict[str, Any]] = [
    {
        "id": "ieee-access",
        "name": "IEEE Access",
        "publisher": "IEEE",
        "scope": [
            "computer science",
            "artificial intelligence",
            "machine learning",
            "engineering",
            "signal processing",
            "telecommunications",
            "interdisciplinary applications",
        ],
        "citation_style": "IEEE (Numbered in brackets e.g. [1])",
        "official_url": "https://ieeeaccess.ieee.org/guide-for-authors/formatting-guidelines/",
        "version_tag": "2026.1",
        "provenance": {
            "source": "IEEE Author Center & IEEE Access Guidelines",
            "last_verified": "2026-09-19",
            "verification_status": "official_curated",
        },
        "rules": [
            {
                "rule_code": "RAG_IEEE_CITATION_STYLE",
                "category": "citation_reference",
                "severity": "critical",
                "requirement_description": "IEEE format requires citations to be numbered consecutively in square brackets [1], [2], corresponding to a numbered references list.",
                "rule_parameters": {"expected_style": "ieee_numbered"},
            },
            {
                "rule_code": "RAG_IEEE_ABSTRACT_LIMIT",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "IEEE Access requires an abstract between 150 and 250 words that does not contain citations or mathematical displays.",
                "rule_parameters": {"min_abstract_words": 150, "max_abstract_words": 250},
            },
            {
                "rule_code": "RAG_IEEE_SCOPE_MATCH",
                "category": "scope_alignment",
                "severity": "major",
                "requirement_description": "Manuscripts submitted to IEEE Access must present original, interdisciplinary, application-oriented or foundational engineering and computing research.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_IEEE_DATA_AVAILABILITY",
                "category": "compliance_formatting",
                "severity": "moderate",
                "requirement_description": "IEEE encourages including a Data Availability Statement specifying the repository or accession details for experimental data.",
                "rule_parameters": {},
            },
        ],
        "chunks": [
            {
                "chunk_index": 0,
                "section_heading": "Citation and Reference Style",
                "content": "IEEE style dictates that references must be numbered in the order of appearance in the manuscript using square brackets [1], [2]. The reference list must contain full author names, publication title, journal/conference venue, volume, issue, page numbers, and DOI where applicable.",
                "source_url": "https://ieeeaccess.ieee.org/guide-for-authors/formatting-guidelines/",
            },
            {
                "chunk_index": 1,
                "section_heading": "Abstract and Keywords Guidelines",
                "content": "An abstract of 150 to 250 words must provide a concise summary of the research questions, methodologies, and quantitative findings. It should not cite references or define uncommon acronyms. Authors should include 4 to 8 index terms or keywords.",
                "source_url": "https://ieeeaccess.ieee.org/guide-for-authors/manuscript-preparation/",
            },
            {
                "chunk_index": 2,
                "section_heading": "Scope and Topical Suitability",
                "content": "IEEE Access publishes peer-reviewed research across all IEEE fields, with an emphasis on interdisciplinary research, computer science, artificial intelligence, communications, and power systems. Theoretical results should be supported by experimental or numerical validation.",
                "source_url": "https://ieeeaccess.ieee.org/about-ieee-access/scope/",
            },
            {
                "chunk_index": 3,
                "section_heading": "Reproducibility and Data Sharing",
                "content": "To foster transparency and reproducible science, authors are urged to provide code repositories (e.g., Code Ocean, GitHub) and data availability statements specifying how datasets can be accessed.",
                "source_url": "https://ieeeaccess.ieee.org/guide-for-authors/data-policy/",
            },
        ],
    },
    {
        "id": "nature-comms",
        "name": "Nature Communications",
        "publisher": "Springer Nature",
        "scope": [
            "multidisciplinary sciences",
            "biological sciences",
            "physics",
            "computational science",
            "materials science",
            "chemistry",
        ],
        "citation_style": "Nature (Sequential numbered with article titles included)",
        "official_url": "https://www.nature.com/ncomms",
        "version_tag": "2026.1",
        "provenance": {
            "source": "Nature Portfolio Editorial Policies",
            "last_verified": "2026-08-15",
            "verification_status": "official_curated",
        },
        "rules": [
            {
                "rule_code": "RAG_NATURE_DATA_AVAILABILITY",
                "category": "manuscript_completeness",
                "severity": "critical",
                "requirement_description": "All Nature Communications articles must include a distinct 'Data Availability' section immediately following the discussion or methods.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_NATURE_CODE_AVAILABILITY",
                "category": "manuscript_completeness",
                "severity": "major",
                "requirement_description": "Manuscripts relying on custom software or algorithms must include an explicit 'Code Availability' statement.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_NATURE_ABSTRACT_UNREFERENCED",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "Nature Communications abstracts must not contain any citation numbers or references.",
                "rule_parameters": {"max_abstract_words": 200},
            },
        ],
        "chunks": [
            {
                "chunk_index": 0,
                "section_heading": "Mandatory Data and Code Availability Statements",
                "content": "A statement on data availability is mandatory for all published papers. Authors must state whether data is deposited in a public repository, available upon request, or included in the supplementary information.",
                "source_url": "https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards",
            },
            {
                "chunk_index": 1,
                "section_heading": "Methodological Rigor and Statistics",
                "content": "Authors must describe statistical tests used, sample sizes, and whether blinding was performed. Error bars must be defined (e.g., standard deviation vs standard error) and p-values explicitly documented.",
                "source_url": "https://www.nature.com/nature-portfolio/editorial-policies",
            },
        ],
    },
    {
        "id": "elsevier-patrec",
        "name": "Pattern Recognition",
        "publisher": "Elsevier",
        "scope": [
            "pattern recognition",
            "computer vision",
            "image processing",
            "machine learning",
            "biometrics",
        ],
        "citation_style": "Numbered or Author-Year (Elsevier standard)",
        "official_url": "https://www.sciencedirect.com/journal/pattern-recognition",
        "version_tag": "2026.1",
        "provenance": {
            "source": "Elsevier Guide for Authors: Pattern Recognition",
            "last_verified": "2026-07-20",
            "verification_status": "official_curated",
        },
        "rules": [
            {
                "rule_code": "RAG_ELSEVIER_CONFLICT_INTEREST",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "Authors must declare any competing financial interests or personal relationships that could influence the work.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_ELSEVIER_SCOPE_ALIGNMENT",
                "category": "scope_alignment",
                "severity": "major",
                "requirement_description": "Submissions must demonstrate theoretical novelty or advanced algorithmic performance in pattern classification, vision, or machine learning.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_ELSEVIER_ABSTRACT_LIMIT",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "Pattern Recognition requires an abstract concise and structured between 100 and 250 words.",
                "rule_parameters": {"min_abstract_words": 100, "max_abstract_words": 250},
            },
        ],
        "chunks": [
            {
                "chunk_index": 0,
                "section_heading": "Declaration of Competing Interests",
                "content": "All manuscripts must include a Declaration of Competing Interest statement. If there are no interests to declare, authors must state: 'The authors declare that they have no known competing financial interests'.",
                "source_url": "https://www.sciencedirect.com/journal/pattern-recognition/publish/guide-for-authors",
            },
            {
                "chunk_index": 1,
                "section_heading": "Algorithmic Validation and Benchmarks",
                "content": "Manuscripts presenting pattern classification techniques must evaluate algorithms on standard public benchmarks (e.g., ImageNet, MNIST, CIFAR) and include statistical significance tests comparing with state-of-the-art baselines.",
                "source_url": "https://www.sciencedirect.com/journal/pattern-recognition/about/aims-and-scope",
            },
        ],
    },
    {
        "id": "acm-csur",
        "name": "ACM Computing Surveys",
        "publisher": "ACM",
        "scope": [
            "computer science",
            "software engineering",
            "algorithms",
            "information systems",
            "artificial intelligence",
            "distributed systems",
            "computing systems",
            "machine learning",
        ],
        "citation_style": "ACM Reference Format (Numbered [1] or Author-Year)",
        "official_url": "https://dl.acm.org/journal/csur",
        "version_tag": "2026.1",
        "provenance": {
            "source": "ACM Author Portal & Computing Surveys Guidelines",
            "last_verified": "2026-09-01",
            "verification_status": "official_curated",
        },
        "rules": [
            {
                "rule_code": "RAG_ACM_DATA_AVAILABILITY",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "ACM encourages artifact evaluation and requires clear statements detailing public repository links or accession terms for research artifacts, software, and datasets.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_ACM_CONFLICT_INTEREST",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "Authors must disclose any personal, professional, or financial conflicts of interest relevant to the survey scope.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_ACM_ABSTRACT_LIMIT",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "ACM Computing Surveys requires an abstract of no more than 250 words outlining the taxonomy and contributions.",
                "rule_parameters": {"min_abstract_words": 100, "max_abstract_words": 250},
            },
        ],
        "chunks": [
            {
                "chunk_index": 0,
                "section_heading": "Artifact and Data Availability Policy",
                "content": "ACM is committed to open and reproducible research. Authors are urged to submit artifacts and provide accessible persistent repositories (e.g., Zenodo, GitHub, Software Heritage) with complete reproduction instructions.",
                "source_url": "https://dl.acm.org/journal/csur/author-guidelines",
            },
            {
                "chunk_index": 1,
                "section_heading": "Scope and Comprehensive Literature Survey Standards",
                "content": "ACM Computing Surveys publishes comprehensive, readable tutorials and surveys that guide readers through complex computer science topics. Submissions must present a rigorous comparative taxonomy and clearly delineate open research directions.",
                "source_url": "https://dl.acm.org/journal/csur/about",
            },
        ],
    },
    {
        "id": "plos-one",
        "name": "PLOS ONE",
        "publisher": "Public Library of Science",
        "scope": [
            "multidisciplinary science",
            "biomedical research",
            "clinical medicine",
            "computational biology",
            "environmental sciences",
            "public health",
            "data science",
        ],
        "citation_style": "PLOS Vancouver (Numbered in brackets e.g. [1])",
        "official_url": "https://journals.plos.org/plosone/s/submission-guidelines",
        "version_tag": "2026.1",
        "provenance": {
            "source": "PLOS ONE Editorial & Publishing Policies",
            "last_verified": "2026-08-30",
            "verification_status": "official_curated",
        },
        "rules": [
            {
                "rule_code": "RAG_PLOS_DATA_AVAILABILITY",
                "category": "compliance_formatting",
                "severity": "critical",
                "requirement_description": "PLOS ONE requires that all data underlying the findings described in the manuscript must be fully available without restriction upon publication in a public repository.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_PLOS_CONFLICT_INTEREST",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "PLOS ONE requires all authors to declare all competing financial and non-financial interests.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_PLOS_ABSTRACT_LIMIT",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "PLOS ONE specifies that abstracts must be less than 300 words and must not cite references.",
                "rule_parameters": {"min_abstract_words": 100, "max_abstract_words": 300},
            },
        ],
        "chunks": [
            {
                "chunk_index": 0,
                "section_heading": "Mandatory Open Data Policy",
                "content": "PLOS ONE requires authors to make all data necessary to replicate the study's findings publicly available without restriction at the time of publication. Acceptable repositories include Dryad, Figshare, Zenodo, or specialized public databases. 'Data available upon request' is not acceptable.",
                "source_url": "https://journals.plos.org/plosone/s/data-availability",
            },
            {
                "chunk_index": 1,
                "section_heading": "Publication Criteria and Methodological Rigor",
                "content": "PLOS ONE evaluates manuscripts based on technical validity and methodological rigor, rather than perceived subjective impact. Studies must report rigorous protocols, appropriate controls, and sufficient statistical documentation.",
                "source_url": "https://journals.plos.org/plosone/s/criteria-for-publication",
            },
        ],
    },
    {
        "id": "oup-bioinformatics",
        "name": "Bioinformatics",
        "publisher": "Oxford University Press",
        "scope": [
            "bioinformatics",
            "computational biology",
            "genomics",
            "machine learning in biology",
            "systems biology",
            "biomedical data science",
            "structural biology",
        ],
        "citation_style": "Oxford Harvard (Author-Year e.g. Smith et al., 2024)",
        "official_url": "https://academic.oup.com/bioinformatics/pages/instructions_for_authors",
        "version_tag": "2026.1",
        "provenance": {
            "source": "Oxford Academic Bioinformatics Author Instructions",
            "last_verified": "2026-08-10",
            "verification_status": "official_curated",
        },
        "rules": [
            {
                "rule_code": "RAG_BIOINFORMATICS_DATA_AVAILABILITY",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "Articles introducing algorithms, software, or pipelines must include an Availability and Implementation statement specifying open-source repository URLs and dependency requirements.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_BIOINFORMATICS_CONFLICT_INTEREST",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "Authors must declare any financial or non-financial conflicts of interest in the manuscript.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_BIOINFORMATICS_ABSTRACT_LIMIT",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "Bioinformatics papers must feature a structured abstract of at most 250 words.",
                "rule_parameters": {"min_abstract_words": 100, "max_abstract_words": 250},
            },
        ],
        "chunks": [
            {
                "chunk_index": 0,
                "section_heading": "Software Availability and Open Source Requirements",
                "content": "Manuscripts presenting novel bioinformatics tools or algorithms must include an Availability and Implementation section specifying the source code URL (e.g., GitHub, GitLab, Bioconductor) under an OSI-approved open source license.",
                "source_url": "https://academic.oup.com/bioinformatics/pages/instructions_for_authors",
            },
            {
                "chunk_index": 1,
                "section_heading": "Topical Scope and Biological Validation",
                "content": "Bioinformatics focuses on new computational algorithms and software that solve concrete biological problems. Methods must be benchmarked on standard biological datasets and compared quantitatively against prevailing state-of-the-art tools.",
                "source_url": "https://academic.oup.com/bioinformatics/pages/about",
            },
        ],
    },
    {
        "id": "aps-prl",
        "name": "Physical Review Letters",
        "publisher": "American Physical Society",
        "scope": [
            "physics",
            "quantum computing",
            "condensed matter",
            "optics",
            "quantum information",
            "computational physics",
            "astrophysics",
            "statistical physics",
        ],
        "citation_style": "APS Physical Review style (Numbered in brackets e.g. [1])",
        "official_url": "https://journals.aps.org/prl/authors",
        "version_tag": "2026.1",
        "provenance": {
            "source": "APS Physics Author Information & PRL Policies",
            "last_verified": "2026-07-15",
            "verification_status": "official_curated",
        },
        "rules": [
            {
                "rule_code": "RAG_APS_DATA_AVAILABILITY",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "APS encourages authors to deposit research data, simulation models, and scripts into publicly accessible repositories with permanent DOIs.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_APS_CONFLICT_INTEREST",
                "category": "compliance_formatting",
                "severity": "major",
                "requirement_description": "Authors must disclose any potential conflicts of interest that could bias the reported results.",
                "rule_parameters": {},
            },
            {
                "rule_code": "RAG_APS_LETTER_BUDGET",
                "category": "compliance_formatting",
                "severity": "critical",
                "requirement_description": "Physical Review Letters enforces a strict 4-page letter length limit and maximum 150-word abstract.",
                "rule_parameters": {"max_pages": 4, "max_abstract_words": 150, "min_pages": 2},
            },
        ],
        "chunks": [
            {
                "chunk_index": 0,
                "section_heading": "Letter Length and Concise Presentation",
                "content": "Physical Review Letters publishes concise, high-impact research. Submissions are subject to a strict 3,750-word length budget (approximately 4 journal pages), requiring crisp theoretical formulation and focused experimental presentation.",
                "source_url": "https://journals.aps.org/prl/authors/length-guide",
            },
            {
                "chunk_index": 1,
                "section_heading": "Data Management and Open Science",
                "content": "APS guidelines encourage open sharing of raw experimental data and computational simulation code in permanent repositories (e.g., Zenodo, HEPData, GitHub) with persistent identifiers to support reproducibility.",
                "source_url": "https://journals.aps.org/prl/authors",
            },
        ],
    },
]


def prepare_seed_embeddings(seeds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Embeds each chunk using the EmbeddingProvider for instant vector retrieval."""
    for journal in seeds:
        for chunk in journal.get("chunks", []):
            if "embedding" not in chunk or not chunk["embedding"]:
                text_to_embed = f"{chunk.get('section_heading', '')} {chunk.get('content', '')}"
                chunk["embedding"] = EmbeddingProvider.get_embedding(text_to_embed)
    return seeds

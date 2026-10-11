import pytest
from app.services.engines.plagiarism import PlagiarismSimilarityEngine


def test_similarity_engine_original_manuscript():
    data = {
        "title": "Quantum Neural Network Architecture",
        "abstract": "This manuscript presents a hybrid quantum-classical optimization method evaluated on synthetic benchmarking datasets. Empirical convergence confirms 94% classification precision with reduced qubit resource overhead.",
        "sections": [
            {
                "number": "I.",
                "title": "Introduction",
                "content": "Quantum computation introduces dimensional scaling advantages for high-dimensional parameter spaces. Traditional gradient descent struggles in barren plateaus.",
            },
            {
                "number": "II.",
                "title": "Methodology",
                "content": "We formulate a parameterized unitary operator acting on n qubits initialized in the zero state. The cost function corresponds to the expectation value of Hamiltonian H.",
            },
        ],
    }

    result = PlagiarismSimilarityEngine.analyze(data)

    assert result["overall_similarity_percent"] <= 14.0
    assert result["risk_level"] == "low"
    assert result["originality_percent"] >= 86.0
    assert "categories" in result
    assert "section_scores" in result
    assert len(result["section_scores"]) >= 2


def test_similarity_engine_boilerplate_manuscript():
    data = {
        "title": "Generic Survey",
        "abstract": "In this paper we propose an autonomous framework.",
        "sections": [
            {
                "number": "I.",
                "title": "Introduction",
                "content": "The remainder of this paper is organized as follows. Recent advancements in deep learning have shown promising results. The experimental results demonstrate that the proposed methodology outperforms baseline models.",
            }
        ],
    }

    result = PlagiarismSimilarityEngine.analyze(data)

    assert result["overall_similarity_percent"] > 20.0
    assert result["risk_level"] in ("moderate", "high")
    assert len(result["flagged_fragments"]) >= 2

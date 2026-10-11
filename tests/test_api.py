import time
import io
import pytest
from main import app
from app.services.orchestrator.runner import AnalysisOrchestrator
from app.models.manuscript import Manuscript
from app.models.user import User


def test_health_endpoints(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    db_res = client.get("/api/v1/db-health")
    assert db_res.status_code == 200
    assert db_res.json()["database_connected"] is True


def test_journals_endpoint(client):
    res = client.get("/api/v1/journals")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3
    journal_ids = [j["id"] for j in data]
    assert "ieee-access" in journal_ids
    assert "nature-comms" in journal_ids


def test_journal_guidelines_endpoint(client):
    res = client.get("/api/v1/journals/ieee-access/guidelines")
    assert res.status_code == 200
    data = res.json()
    assert data["journal_id"] == "ieee-access"
    assert len(data["rules"]) >= 2
    assert len(data["chunks"]) >= 2


def test_upload_invalid_file(client):
    # Empty file
    res = client.post(
        "/api/v1/manuscripts/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert res.status_code == 400

    # Disallowed extension
    res_ext = client.post(
        "/api/v1/manuscripts/upload",
        files={"file": ("virus.exe", b"malicious", "application/octet-stream")},
    )
    assert res_ext.status_code == 400


def test_end_to_end_analysis_pipeline(client, db_session, valid_pdf_bytes):
    # 1. Upload manuscript
    upload_res = client.post(
        "/api/v1/manuscripts/upload",
        files={"file": ("research_paper.pdf", valid_pdf_bytes, "application/pdf")},
        data={"title": "Multi-Engine Paper Verification"},
    )
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    manuscript_id = upload_data["manuscript_id"]
    version_id = upload_data["version_id"]
    assert manuscript_id is not None

    # 2. Trigger analysis (returns 202)
    analyze_res = client.post(
        f"/api/v1/manuscripts/{manuscript_id}/analyze",
        json={"journal_id": "ieee-access"},
    )
    assert analyze_res.status_code == 202
    analyze_data = analyze_res.json()
    analysis_id = analyze_data["analysis_id"]

    # 3. Synchronously run or wait for orchestrator to complete in test environment
    AnalysisOrchestrator.execute_analysis(db=db_session, job_id=analysis_id)

    # 4. Check status
    status_res = client.get(f"/api/v1/analysis/{analysis_id}")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "completed"
    assert status_res.json()["progress_percent"] == 100

    # 5. Get structured findings
    results_res = client.get(f"/api/v1/analysis/{analysis_id}/results")
    assert results_res.status_code == 200
    assert len(results_res.json()["runs"]) == 3

    # 6. Get Complete Report
    report_res = client.get(f"/api/v1/analysis/{analysis_id}/report")
    assert report_res.status_code == 200
    report_data = report_res.json()
    assert report_data["manuscript_title"] == "Multi-Engine Paper Verification"
    assert report_data["readiness_score"]["overall_score"] > 60.0
    assert "category_scores" in report_data["readiness_score"]
    assert len(report_data["actionable_recommendations"]) >= 1

    # 7. Export as PDF
    pdf_res = client.get(f"/api/v1/analysis/{analysis_id}/export?format=pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000

    # 8. Export as DOCX
    docx_res = client.get(f"/api/v1/analysis/{analysis_id}/export?format=docx")
    assert docx_res.status_code == 200
    assert "wordprocessingml" in docx_res.headers["content-type"]
    assert len(docx_res.content) > 1000


def test_tenant_isolation(client, db_session, valid_pdf_bytes):
    # Upload manuscript as user A
    upload_res = client.post(
        "/api/v1/manuscripts/upload",
        files={"file": ("tenant_test.pdf", valid_pdf_bytes, "application/pdf")},
    )
    m_id = upload_res.json()["manuscript_id"]

    # Create another user B
    user_b = User(
        id="99999999-9999-9999-9999-999999999999",
        email="other_researcher@mit.edu",
        hashed_password="pw",
        full_name="Dr. Other",
        is_active=True,
    )
    db_session.add(user_b)
    db_session.commit()

    # Query with user B override
    from app.api.deps import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user_b

    # User B should NOT be able to view user A's manuscript (returns 404)
    forbidden_res = client.get(f"/api/v1/manuscripts/{m_id}")
    assert forbidden_res.status_code == 404

    app.dependency_overrides.clear()

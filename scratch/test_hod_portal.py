import pytest
from app import app
from database.db import get_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_admin_login(client):
    res = client.post("/login", data={"username": "admin001", "password": "Admin@123"}, follow_redirects=False)
    assert res.status_code == 302
    assert "/admin" in res.headers["Location"]

def test_faculty_login(client):
    res = client.post("/login", data={"username": "faculty001", "password": "Faculty@123"}, follow_redirects=False)
    assert res.status_code == 302
    assert "/faculty" in res.headers["Location"]

def test_student_login(client):
    res = client.post("/login", data={"username": "student001", "password": "Student@123"}, follow_redirects=False)
    assert res.status_code == 302
    assert "/student" in res.headers["Location"]

def test_hod_cse_login_and_overview(client):
    # 1. Login as HOD CSE
    res = client.post("/login", data={"username": "hod_cse", "password": "Hod@123"}, follow_redirects=False)
    assert res.status_code == 302
    assert "/hod" in res.headers["Location"]

    # 2. Access /hod/dashboard
    res = client.get("/hod")
    assert res.status_code == 200
    assert b"HOD Portal" in res.data
    assert b"CSE" in res.data

    # 3. Access /api/hod/overview
    res = client.get("/api/hod/overview")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["department"]["code"] == "CSE"
    assert data["metrics"]["total_students"] > 0
    assert data["metrics"]["total_faculty"] > 0
    assert "Faculty attendance data is not available in the current system." in data["faculty"]["attendance_notice"]

    # Verify all students returned belong strictly to CSE
    for s in data["students"]:
        assert s["department"].upper() == "CSE"

    # Verify all faculty returned belong strictly to CSE
    for f in data["faculty"]["list"]:
        assert f["department"].upper() == "CSE"

def test_hod_cross_department_security(client):
    # Login as HOD CSE
    client.post("/login", data={"username": "hod_cse", "password": "Hod@123"})

    # Try to access AIML student (CIQ-DEMO-AIML-01) -> must be rejected with 403
    res = client.get("/api/students/CIQ-DEMO-AIML-01")
    assert res.status_code == 403

    # Try to access CSE student (CIQ-2026-001) -> must succeed with 200
    res = client.get("/api/students/CIQ-2026-001")
    assert res.status_code == 200
    assert res.get_json()["student_id"] == "CIQ-2026-001"

    # Try to access Admin-only overview API -> must be rejected with 403
    res = client.get("/api/admin/overview")
    assert res.status_code == 403

    # Try to access Admin dashboard view -> redirected away
    res = client.get("/admin", follow_redirects=False)
    assert res.status_code == 302
    assert "/hod" in res.headers["Location"]

def test_hod_aiml_login_and_security(client):
    # Login as HOD AIML
    res = client.post("/login", data={"username": "hod_aiml", "password": "Hod@123"}, follow_redirects=False)
    assert res.status_code == 302
    assert "/hod" in res.headers["Location"]

    # Access HOD overview -> department is AIML
    res = client.get("/api/hod/overview")
    assert res.status_code == 200
    data = res.get_json()
    assert data["department"]["code"] == "AIML"

    # All returned students must be AIML
    for s in data["students"]:
        assert s["department"].upper() == "AIML"

    # Try to access CSE student (CIQ-2026-001) -> must be rejected with 403
    res = client.get("/api/students/CIQ-2026-001")
    assert res.status_code == 403

    # Try to access AIML student (CIQ-DEMO-AIML-01) -> must succeed with 200
    res = client.get("/api/students/CIQ-DEMO-AIML-01")
    assert res.status_code == 200

def test_hod_export_csv_restricted(client):
    # Login as HOD CSE
    client.post("/login", data={"username": "hod_cse", "password": "Hod@123"})

    # Even if passing ?department=AIML in query, server-side enforcement forces CSE
    res = client.get("/api/export/csv?department=AIML")
    assert res.status_code == 200
    csv_text = res.data.decode("utf-8")
    lines = [l for l in csv_text.splitlines() if l.strip()]
    # Skip header line, check all rows belong to CSE
    assert len(lines) > 1
    for row in lines[1:]:
        assert "CSE" in row
        assert "AIML" not in row

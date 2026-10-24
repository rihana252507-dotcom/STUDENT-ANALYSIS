import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app
from database.db import get_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_hod_authentication_all_departments(client):
    """Verifies that HODs for all departments can authenticate and access HOD dashboard."""
    hod_accounts = [
        ("hod_cse", "CSE"),
        ("hod_it", "IT"),
        ("hod_ece", "ECE"),
        ("hod_aiml", "AIML"),
        ("hod_aids", "AI&DS"),
        ("hod_me", "ME"),
    ]
    for uid, dept in hod_accounts:
        client.get("/logout")
        # 1. Login with JSON
        resp = client.post("/login", json={"user_id": uid, "password": "Hod@123"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["role"] == "hod"
        assert data["department"] == dept

        # 2. Access dashboard
        dash_resp = client.get("/hod")
        assert dash_resp.status_code == 200
        html = dash_resp.data.decode("utf-8")
        assert "studentDetailModal" in html
        assert "loadHodDashboard" in html

        # 3. Access overview API
        api_resp = client.get("/api/hod/overview")
        assert api_resp.status_code == 200
        overview = api_resp.get_json()
        assert overview["department"]["code"] == dept

def test_hod_invalid_credentials_rejected(client):
    """Verifies invalid passwords or usernames are rejected without leaking info."""
    client.get("/logout")
    resp = client.post("/login", json={"user_id": "hod_cse", "password": "WrongPassword"})
    assert resp.status_code == 401
    assert "Invalid User ID or Password" in resp.get_json()["message"]

def test_hod_unauthenticated_and_role_protection(client):
    """Verifies unauthenticated and non-HOD users cannot access HOD endpoints."""
    client.get("/logout")
    # Unauthenticated
    resp = client.get("/hod")
    assert resp.status_code == 302
    resp_api = client.get("/api/hod/overview")
    assert resp_api.status_code == 401

    # Student trying to access HOD
    client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    resp_stud = client.get("/hod")
    assert resp_stud.status_code == 302  # redirects to student dashboard
    resp_stud_api = client.get("/api/hod/overview")
    assert resp_stud_api.status_code == 403

    # Faculty trying to access HOD
    client.get("/logout")
    client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    resp_fac = client.get("/hod")
    assert resp_fac.status_code == 302  # redirects to faculty dashboard
    resp_fac_api = client.get("/api/hod/overview")
    assert resp_fac_api.status_code == 403

def test_hod_department_security_and_isolation(client):
    """Verifies that an HOD cannot view or modify data outside their assigned department."""
    client.get("/logout")
    # Log in as HOD CSE
    client.post("/login", json={"user_id": "hod_cse", "password": "Hod@123"})

    # 1. Overview API only contains CSE records
    overview = client.get("/api/hod/overview").get_json()
    assert overview["department"]["code"] == "CSE"
    for s in overview["students"]:
        assert s["department"].upper() == "CSE"
    for f in overview["faculty"]["list"]:
        assert f["department"].upper() == "CSE"

    # 2. Can inspect student from CSE (CIQ-2026-001)
    cse_st = client.get("/api/students/CIQ-2026-001")
    assert cse_st.status_code == 200
    st_data = cse_st.get_json()
    assert st_data["department"].upper() == "CSE"

    # 3. Cannot inspect student from IT (CIQ-2026-002)
    it_st = client.get("/api/students/CIQ-2026-002")
    assert it_st.status_code == 403
    assert "Access denied" in it_st.get_json()["message"]

    # 4. Cannot log intervention for IT student
    bad_intv = client.post("/api/students/CIQ-2026-002/intervention", json={
        "title": "Unauthorized Counseling",
        "priority": "High"
    })
    assert bad_intv.status_code == 403

    # 5. Can log intervention for CSE student (HTTP 201 Created)
    good_intv = client.post("/api/students/CIQ-2026-001/intervention", json={
        "title": "HOD Academic Counseling Checkpoint",
        "priority": "High",
        "instructions": "Discuss semester backlog strategy"
    })
    assert good_intv.status_code in (200, 201)

def test_hod_exports(client):
    """Verifies all 6 HOD export endpoints succeed with valid Content-Type."""
    client.get("/logout")
    client.post("/login", json={"user_id": "hod_cse", "password": "Hod@123"})

    csv_students = client.get("/api/hod/export/students/csv")
    assert csv_students.status_code == 200
    assert "text/csv" in csv_students.headers.get("Content-Type", "")

    xlsx_students = client.get("/api/hod/export/students/xlsx")
    assert xlsx_students.status_code == 200

    csv_faculty = client.get("/api/hod/export/faculty/csv")
    assert csv_faculty.status_code == 200
    assert "text/csv" in csv_faculty.headers.get("Content-Type", "")

    xlsx_faculty = client.get("/api/hod/export/faculty/xlsx")
    assert xlsx_faculty.status_code == 200

    csv_summary = client.get("/api/hod/export/summary/csv")
    assert csv_summary.status_code == 200
    assert "text/csv" in csv_summary.headers.get("Content-Type", "")

    xlsx_summary = client.get("/api/hod/export/summary/xlsx")
    assert xlsx_summary.status_code == 200

def test_regression_admin_faculty_student_logins(client):
    """Regression test ensuring Admin, Faculty, and Student portals remain fully operational."""
    # 1. Admin
    client.get("/logout")
    admin_login = client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    assert admin_login.status_code == 200
    admin_dash = client.get("/admin")
    assert admin_dash.status_code == 200

    # 2. Faculty
    client.get("/logout")
    fac_login = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert fac_login.status_code == 200
    fac_dash = client.get("/faculty")
    assert fac_dash.status_code == 200

    # 3. Student
    client.get("/logout")
    stud_login = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert stud_login.status_code == 200
    stud_dash = client.get("/student")
    assert stud_dash.status_code == 200

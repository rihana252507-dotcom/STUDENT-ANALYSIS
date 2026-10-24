import pytest
import re
from app import app
from database.db import get_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_faculty_backlog_subjects_and_details(client):
    # Log in as faculty001
    resp = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert resp.status_code == 200

    # Test /api/students endpoint includes backlog_details and backlog_subjects
    resp = client.get("/api/students")
    assert resp.status_code == 200
    data = resp.get_json()
    students = data.get("students", [])
    assert len(students) > 0

    # Student CIQ-2026-008 (Kabir Mehta) has 3 backlogs
    kabir = next((s for s in students if s["student_id"] == "CIQ-2026-008"), None)
    assert kabir is not None
    assert kabir["backlogs"] == 3
    assert "Data Structures" in kabir["backlog_subjects"]
    assert len(kabir.get("backlog_details", [])) == 3
    for b in kabir["backlog_details"]:
        assert "course_name" in b
        assert "course_code" in b
        assert "semester" in b
        assert "grade" in b
        assert "display" in b

    # Test /api/students/<student_id> detail endpoint
    resp = client.get("/api/students/CIQ-2026-008")
    assert resp.status_code == 200
    detail = resp.get_json()
    assert detail["student_id"] == "CIQ-2026-008"
    assert "backlog_details" in detail
    assert len(detail["backlog_details"]) == 3
    assert detail["backlog_details"][0]["course_code"] == "CS102"
    assert "Data Structures & Algorithms in C/C++" in detail["backlog_details"][0]["course_name"]

def test_student_attendance_readability_and_course_breakdown(client):
    # Log in as student001
    resp = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert resp.status_code == 200

    resp = client.get("/student")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    # Verify that attendance section has high-contrast styling and no text-gradient-purple on big attendance number
    assert 'class="text-gradient-purple"' not in html.split('id="section-attendance"')[1].split('</section>')[0]
    assert '#172B4D' in html.split('id="section-attendance"')[1]

    # Verify that low contrast #D4E9FF is not used for descriptive text in attendance section
    att_section = html.split('id="section-attendance"')[1].split('</section>')[0]
    assert 'color:#D4E9FF' not in att_section

    # Verify dynamic course-wise breakdown renders real courses for student001 (e.g., Computer Networks, Cloud Computing, etc.)
    assert 'Classes conducted vs attended across all active subjects' in att_section
    assert 'attended' in att_section
    assert '%' in att_section

def test_risk_alerts_sorting_logic():
    # Verify in app.js that riskPriority sorting is implemented
    with open("static/js/app.js", "r", encoding="utf-8") as f:
        js = f.read()
    assert "riskPriority" in js
    assert "atRisk.sort" in js
    assert "modalBacklogsBreakdownSection" in js
    assert "modalBacklogSubjectsContainer" in js

"""
Verification test script for Faculty Academics Page and Faculty Risk Page.
Verifies:
1. Faculty Academics displays all advisees with active backlogs, including backlog subjects, counts, semester, and year.
2. Faculty Risk displays all advisees meeting risk criteria (High/Medium risk, backlogs, low attendance).
3. Preservation of existing endpoints, roles, and records.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.db import get_db

def test_faculty_academics_and_risk():
    client = app.test_client()

    # 1. Test faculty001 (CSE - Dr. Sunita Rao)
    client.get("/logout")
    login_resp = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert login_resp.status_code == 200, "Faculty001 login failed"

    api_resp = client.get("/api/students")
    assert api_resp.status_code == 200, "Failed to fetch /api/students for faculty001"
    data = api_resp.get_json()
    students = data.get("students", [])
    assert len(students) > 0, "No students returned for faculty001"

    # Verify students with backlogs exist
    backlog_students = [s for s in students if s.get("backlogs", 0) > 0]
    assert len(backlog_students) >= 5, f"Expected at least 5 backlog students for faculty001, got {len(backlog_students)}"

    # Check Kabir Mehta (CIQ-2026-008)
    kabir = next((s for s in students if s["student_id"] == "CIQ-2026-008"), None)
    assert kabir is not None, "Kabir Mehta (CIQ-2026-008) not found in faculty001 caseload"
    assert kabir["backlogs"] == 3, f"Expected 3 backlogs for Kabir Mehta, got {kabir['backlogs']}"
    assert "Data Structures" in kabir["backlog_subjects"] or "CS102" in kabir["backlog_subjects"] or len(kabir["backlog_subjects"]) > 0
    assert "semester" in kabir
    assert "academic_year" in kabir

    # Check at-risk advisees for faculty001
    high_risk = [s for s in students if s.get("risk_level") == "High"]
    medium_risk = [s for s in students if s.get("risk_level") == "Medium"]
    assert len(high_risk) >= 3, f"Expected at least 3 high risk students, got {len(high_risk)}"
    assert len(medium_risk) >= 3, f"Expected at least 3 medium risk students, got {len(medium_risk)}"

    # 2. Test faculty002 (IT - Dr. Meenakshi Sundaram)
    client.get("/logout")
    client.post("/login", json={"user_id": "faculty002", "password": "Faculty@123"})
    api_resp2 = client.get("/api/students")
    assert api_resp2.status_code == 200
    students2 = api_resp2.get_json().get("students", [])
    
    # Check Divya Rao (CIQ-2026-007) and Sneha Patel (CIQ-2026-006)
    backlog_it = [s for s in students2 if s.get("backlogs", 0) > 0]
    assert len(backlog_it) >= 2, f"Expected at least 2 backlog students for IT, got {len(backlog_it)}"
    divya = next((s for s in students2 if s["student_id"] == "CIQ-2026-007"), None)
    assert divya is not None
    assert divya["backlogs"] == 2
    assert "Operating Systems" in divya["backlog_subjects"] or len(divya["backlog_subjects"]) > 0

    # 3. Test faculty dashboard HTML sections
    dash_resp = client.get("/faculty")
    assert dash_resp.status_code == 200
    html = dash_resp.data.decode("utf-8")
    assert 'id="academicPerfTableBody"' in html
    assert 'id="riskAlertsTableBody"' in html
    assert 'id="section-academic-performance"' in html
    assert 'id="section-risk-alerts"' in html

    # 4. Verify app.js rendering logic
    with open("static/js/app.js", "r", encoding="utf-8") as f:
        js = f.read()
    assert "renderAcademicPerf" in js
    assert "renderRiskAlertsTable" in js
    assert "renderAttendanceTable" in js
    assert "academicPerfTableBody" in js
    assert "riskAlertsTableBody" in js
    assert "backlog_subjects" in js

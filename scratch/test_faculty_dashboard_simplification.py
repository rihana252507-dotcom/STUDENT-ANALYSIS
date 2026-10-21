"""
Verification test suite for:
Task: Simplify Faculty Dashboard with Three Graphical Student Analytics Indicators
1. Faculty login & Dashboard loads successfully (200).
2. The three graphical indicators (Student Attendance, Student Backlogs, Student Academic Risk) are present on section-overview.
3. The student names table / list (Advisee Quick Roster / facultyOverviewTableBody) is removed from the visible layout of the main dashboard.
4. Attendance average, backlog counts, and risk distribution are based on assigned students.
5. Preserves Admin, Student, Notifications, Chatbot, and other dashboards/endpoints.
"""
import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app
from database.db import get_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)

def test_01_faculty_dashboard_three_graphical_indicators_present(client):
    """Verify that logging in as Faculty displays the three graphical indicators in section-overview."""
    login(client, "faculty001", "Faculty@123")
    res = client.get("/faculty")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    # Extract section-overview
    assert '<section id="section-overview"' in html
    overview_html = html.split('<section id="section-overview"')[1].split('</section>')[0]

    # Verify 3 Indicator Titles
    assert "Student Attendance" in overview_html
    assert "Student Backlogs" in overview_html
    assert "Student Academic Risk" in overview_html

    # Verify Indicator markup elements
    assert 'id="facultyAnalyticsIndicatorsRow"' in overview_html
    assert 'id="facultyAttCircleProgress"' in overview_html
    assert 'id="facultyBacklogCircleProgress"' in overview_html
    assert 'id="facultyRiskDoughnutChart"' in overview_html

def test_02_student_names_table_removed_from_overview(client):
    """Verify the student names table / roster is removed from the main Faculty Dashboard (section-overview)."""
    login(client, "faculty001", "Faculty@123")
    res = client.get("/faculty")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    overview_html = html.split('<section id="section-overview"')[1].split('</section>')[0]

    # The student names roster table must NOT be in section-overview
    assert "facultyOverviewTableBody" not in overview_html
    assert "Assigned Advisees Overview" not in overview_html

def test_03_faculty_api_returns_assigned_students(client):
    """Verify /api/students returns only assigned students for logged-in Faculty."""
    login(client, "faculty001", "Faculty@123")
    res = client.get("/api/students")
    assert res.status_code == 200
    data = res.get_json()
    students = data.get("students", [])
    assert len(students) > 0
    # All returned students belong to faculty001 or CSE
    for s in students:
        assert s["faculty_id"] == "faculty001" or s["department"] == "CSE"

def test_04_fallback_messages_defined_in_template(client):
    """Verify appropriate fallback text when data is unavailable."""
    login(client, "faculty001", "Faculty@123")
    res = client.get("/faculty")
    html = res.data.decode("utf-8")
    overview_html = html.split('<section id="section-overview"')[1].split('</section>')[0]

    assert "Attendance data unavailable" in overview_html
    assert "Backlog data unavailable" in overview_html
    assert "Risk assessment unavailable" in overview_html
    assert "No assigned student records are available for analytics yet." in overview_html

def test_05_admin_dashboard_unaffected(client):
    """Verify Admin dashboard still functions with its student tables."""
    login(client, "admin001", "Admin@123")
    res = client.get("/admin")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "studentsTableBody" in html
    assert "riskWatchlistBody" in html

def test_06_student_dashboard_unaffected(client):
    """Verify Student dashboard still functions."""
    login(client, "student001", "Student@123")
    res = client.get("/student")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "section-my-dashboard" in html
    assert "Aarav Reddy" in html

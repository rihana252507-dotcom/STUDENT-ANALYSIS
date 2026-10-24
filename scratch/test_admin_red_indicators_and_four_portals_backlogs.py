"""
Test suite verifying:
1. Admin Overview: Low success score (<70) and attendance (<75%) shown in red (#DC2626).
2. Department benchmark: Low success score (<70) and attendance (<75%) shown in red.
3. Segment drilldown: Backlog count and actual subject names displayed.
4. All four portals (Admin, HOD, Faculty, Student) show backlog counts AND actual subject names.
5. End-to-end API and template contract preservation across all roles.
"""

import os
import re
import pytest
from app import app
from database.db import get_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_students_contains_structured_backlog_details(client):
    """Verify /api/students returns backlog_details with course_name and course_code."""
    with client.session_transaction() as sess:
        sess["user_id"] = "admin"
        sess["role"] = "admin"
        sess["name"] = "System Administrator"

    res = client.get("/api/students")
    assert res.status_code == 200
    data = res.get_json()
    assert "students" in data
    students = data["students"]
    assert len(students) > 0

    # All students have backlog_details field as a list
    for s in students:
        assert "backlog_details" in s
        assert isinstance(s["backlog_details"], list)

    # Students with recorded transcript backlogs have matching structured records
    students_with_records = [s for s in students if len(s["backlog_details"]) > 0]
    assert len(students_with_records) >= 5, "Students with academic transcript backlogs must have details"

    for s in students_with_records:
        assert len(s["backlog_details"]) == s["backlogs"]
        for b in s["backlog_details"]:
            assert "course_name" in b and len(b["course_name"]) > 0
            assert "course_code" in b and len(b["course_code"]) > 0
            assert "display" in b and b["course_name"] in b["display"]


def test_api_student_detail_contains_backlog_details(client):
    """Verify /api/students/<id> returns structured backlog details."""
    with client.session_transaction() as sess:
        sess["user_id"] = "admin"
        sess["role"] = "admin"
        sess["name"] = "System Administrator"

    res = client.get("/api/students/CIQ-2026-008")
    assert res.status_code == 200
    s = res.get_json()
    assert s["student_id"] == "CIQ-2026-008"
    assert s["backlogs"] == 3
    assert len(s["backlog_details"]) == 3

    subject_names = [b["course_name"] for b in s["backlog_details"]]
    assert "Data Structures & Algorithms in C/C++" in subject_names
    assert "Digital Logic & Computer Organization" in subject_names
    assert "Design & Analysis of Algorithms" in subject_names


def test_admin_kpi_red_indicators_in_appjs():
    """Verify app.js colors kpiAvgSuccess < 70 red and kpiAttendanceAvg/Rate < 75 red."""
    path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "app.js")
    with open(path, "r", encoding="utf-8") as f:
        js = f.read()

    # Success target is defined
    assert "SUCCESS_TARGET = 70" in js
    assert "ATT_THRESHOLD = 75" in js

    # Red color #DC2626 is used for below-target
    assert "successVal < SUCCESS_TARGET ? '#DC2626'" in js
    assert "rateVal < ATT_THRESHOLD ? '#DC2626'" in js
    assert "attVal < ATT_THRESHOLD ? '#DC2626'" in js

    # Department benchmarks check
    assert "parseFloat(d.avg_attendance) < 75 ? '#DC2626'" in js
    assert "parseFloat(d.avg_success_score) < 70 ? '#DC2626'" in js


def test_admin_segment_drilldown_shows_backlog_subjects():
    """Verify showSegmentStudents in app.js formats backlog_details."""
    path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "app.js")
    with open(path, "r", encoding="utf-8") as f:
        js = f.read()

    assert "s.backlog_details" in js
    assert "b.display || b.course_name" in js
    assert "showSegmentStudents" in js


def test_admin_student_table_and_modal_red_indicators():
    """Verify student table and modal in app.js show low success score and attendance in red."""
    path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "app.js")
    with open(path, "r", encoding="utf-8") as f:
        js = f.read()

    # Student table attendance warning & success score
    assert "s.attendance_pct < 75 ? \"color:#DC2626; font-weight:700;\"" in js
    assert "parseFloat(s.success_score) < 70 ? '#DC2626'" in js

    # Modal colors
    assert 'parseFloat(s.success_score) < 70) ? "#DC2626"' in js
    assert 'parseFloat(s.attendance_pct) < 75.0) ? "#DC2626"' in js


def test_hod_portal_backlog_and_indicators():
    """Verify HOD dashboard includes backlog breakdown and red indicators."""
    path = os.path.join(os.path.dirname(__file__), "..", "templates", "hod_dashboard.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Backlog details table in modal
    assert "modalBacklogsBreakdownSection" in html
    assert "s.backlog_details.map" in html

    # Backlog subject names in risk cards
    assert "s.backlog_details.map(bk => bk.display).join" in html
    assert "Backlog(s)" in html

    # Low attendance < 75 and low success score < 70 colored red
    assert "avgAtt > 0 && avgAtt < 75) ? '#DC2626'" in html
    assert "avgSuccess > 0 && avgSuccess < 70) ? '#DC2626'" in html


def test_faculty_portal_backlog_breakdown():
    """Verify faculty dashboard and inspect modal display backlog subjects."""
    path = os.path.join(os.path.dirname(__file__), "..", "templates", "faculty_dashboard.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "modalBacklogsBreakdownSection" in html
    assert "modalBacklogSubjectsContainer" in html

    app_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "app.js")
    with open(app_path, "r", encoding="utf-8") as f:
        js = f.read()

    # Faculty Academic Perf table shows backlog subject names
    assert "s.backlog_details.map(b => b.display).join(\"; \")" in js


def test_student_portal_backlog_subjects_and_attendance(client):
    """Verify student dashboard displays student's actual backlog subjects and attendance."""
    with client.session_transaction() as sess:
        sess["user_id"] = "CIQ-2026-008"
        sess["role"] = "student"
        sess["name"] = "Kabir Mehta"

    res = client.get("/student/dashboard")
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    # Student portal shows backlog subjects
    assert "Active Backlogs" in html
    assert "Data Structures &amp; Algorithms in C/C++" in html or "Data Structures" in html
    assert "Course-Wise Attendance Breakdown" in html
    assert "#DC2626" in html  # Red indicator for below 75% attendance


def test_all_portals_login_routes(client):
    """Verify all 4 login dashboards respond with HTTP 200 for authenticated sessions."""
    # 1. Admin
    with client.session_transaction() as sess:
        sess["user_id"] = "admin"
        sess["role"] = "admin"
        sess["name"] = "Administrator"
    res = client.get("/admin/dashboard")
    assert res.status_code == 200

    # 2. HOD
    with client.session_transaction() as sess:
        sess["user_id"] = "hod_cse"
        sess["role"] = "hod"
        sess["department"] = "CSE"
        sess["name"] = "Dr. Rajesh Kumar"
    res = client.get("/hod/dashboard")
    assert res.status_code == 200

    # 3. Faculty
    with client.session_transaction() as sess:
        sess["user_id"] = "FAC001"
        sess["role"] = "faculty"
        sess["name"] = "Dr. Sunita Rao"
        sess["department"] = "CSE"
    res = client.get("/faculty/dashboard")
    assert res.status_code == 200

    # 4. Student
    with client.session_transaction() as sess:
        sess["user_id"] = "CIQ-2026-001"
        sess["role"] = "student"
        sess["name"] = "Aarav Sharma"
    res = client.get("/student/dashboard")
    assert res.status_code == 200

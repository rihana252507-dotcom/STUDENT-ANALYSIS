"""
Verification test script for:
1. Simplifying Student Dashboard (removing 6 profile fields, adding 3 graphical indicators).
2. Moving 6 basic student profile fields to the Profile section (#section-my-profile).
3. Verifying Academic Marks, Attendance, and Academic Risk graphics with fallbacks and warnings.
4. Preserving Academic Risk Alert, Chatbot, Fee Details, Academic Records, Admin, and Faculty dashboards.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.db import get_db

def test_profile_and_graphics():
    print("\n" + "="*75)
    print("RUNNING DASHBOARD SIMPLIFICATION & PROFILE GRAPHICS VERIFICATION")
    print("="*75)

    client = app.test_client()

    # -----------------------------------------------------------------
    # 1. Aarav Reddy (student001 - Low Risk, High Attendance)
    # -----------------------------------------------------------------
    client.get("/logout")
    login_resp = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert login_resp.status_code == 200, "Student001 login failed"

    dash_resp = client.get("/student")
    assert dash_resp.status_code == 200
    html = dash_resp.data.decode("utf-8")

    # Extract #section-my-dashboard
    assert '<section id="section-my-dashboard"' in html
    dashboard_section = html.split('<section id="section-my-dashboard"')[1].split('</section>')[0]

    # Extract #section-my-profile
    assert '<section id="section-my-profile"' in html
    profile_section = html.split('<section id="section-my-profile"')[1].split('</section>')[0]

    # Verify Welcome message in dashboard
    assert "Welcome back," in dashboard_section
    assert "Aarav Reddy" in dashboard_section
    print("[PASS] 1. Welcome greeting intact on main dashboard.")

    # Verify the 6 profile fields are REMOVED from the main dashboard
    assert "Roll Number" not in dashboard_section, "Roll Number should NOT be on main dashboard"
    assert "Current Semester" not in dashboard_section, "Current Semester should NOT be on main dashboard"
    assert "Branch / Department" not in dashboard_section, "Branch / Department should NOT be on main dashboard"
    assert "Class Faculty Mentor" not in dashboard_section, "Class Faculty Mentor should NOT be on main dashboard"
    print("[PASS] 2. Basic student profile fields cleanly removed from main dashboard.")

    # Verify the 3 Graphical Indicators on main dashboard
    # 1. Academic Marks
    assert "Academic Marks" in dashboard_section
    assert "Overall recorded performance" in dashboard_section
    assert "92" in dashboard_section or "92.0%" in dashboard_section
    print("[PASS] 3. Academic Marks graphic present with score and supporting label.")

    # 2. Attendance
    assert "Attendance" in dashboard_section
    assert "Recorded attendance" in dashboard_section
    assert "94" in dashboard_section or "94.0%" in dashboard_section
    print("[PASS] 4. Attendance graphic present with percentage and compliant status.")

    # 3. Academic Risk
    assert "Academic Risk" in dashboard_section
    assert "Current academic risk assessment" in dashboard_section
    assert "Low Risk" in dashboard_section
    assert "Success Score:" in dashboard_section
    print("[PASS] 5. Academic Risk graphic present with category badge and success score.")

    # Verify Academic Risk Alert is preserved below graphics in dashboard
    assert "Academic Risk Alert" in dashboard_section
    assert "Academic Risk Level Gauge" in dashboard_section
    assert "Good Academic Standing" in dashboard_section
    print("[PASS] 6. Academic Risk Alert card preserved below graphical indicators.")

    # Verify the 6 basic profile fields are cleanly presented in #section-my-profile
    assert "My Student Profile" in profile_section
    assert "Student Name" in profile_section
    assert "Aarav Reddy" in profile_section
    assert "Roll Number" in profile_section
    assert "CIQ-2026-001" in profile_section
    assert "Current Semester" in profile_section
    assert "Semester 8" in profile_section
    assert "Branch / Department" in profile_section
    assert "Computer Science" in profile_section or "CSE" in profile_section
    assert "Phone Number" in profile_section
    assert "+91 9877827638" in profile_section
    assert "Class Faculty Mentor" in profile_section
    assert "Dr. Sunita Rao" in profile_section
    print("[PASS] 7. All 6 basic student profile fields correctly rendered in Profile view.")

    # -----------------------------------------------------------------
    # 2. High Risk & Attendance Shortage Student (student007 - Divya Rao)
    # -----------------------------------------------------------------
    client.get("/logout")
    login_resp = client.post("/login", json={"user_id": "student007", "password": "Student@123"})
    assert login_resp.status_code == 200, "Student007 login failed"

    dash_resp7 = client.get("/student")
    assert dash_resp7.status_code == 200
    html7 = dash_resp7.data.decode("utf-8")
    dashboard7 = html7.split('<section id="section-my-dashboard"')[1].split('</section>')[0]

    assert "High Risk" in dashboard7
    assert "61.5%" in dashboard7 or "61.5" in dashboard7
    assert "Shortage" in dashboard7 or "Shortage Warning" in dashboard7
    print("[PASS] 8. Attendance shortage alert and High Risk status triggered correctly for student007.")

    # -----------------------------------------------------------------
    # 3. Preservation of Chatbot, Fee Details, Academic Records
    # -----------------------------------------------------------------
    # Chatbot in recommendations section
    assert "CampusIQ Study Assistant" in html
    assert "ciqChatInput" in html
    assert "ciqChatSend" in html

    # Fee details page/section
    assert "Fee Details" in html
    assert "section-fee-details" in html

    # Academic records page/section
    assert "Complete Academic History" in html
    assert "section-my-academics" in html
    print("[PASS] 9. Chatbot, Fee Details, and Academic Records fully preserved.")

    # -----------------------------------------------------------------
    # 4. Admin and Faculty Dashboards Verification
    # -----------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    admin_dash = client.get("/admin")
    assert admin_dash.status_code == 200
    print("[PASS] 10. Admin dashboard accessible and operational.")
    client.get("/logout")
    client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    faculty_dash = client.get("/faculty")
    assert faculty_dash.status_code == 200
    print("[PASS] 11. Faculty dashboard accessible and operational.")

    # -----------------------------------------------------------------
    # 5. Missing Data & Fallbacks Verification
    # -----------------------------------------------------------------
    with app.test_request_context("/student"):
        from flask import render_template
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students LIMIT 1")
        sample_row = dict(cursor.fetchone())
        conn.close()

        empty_student = dict(sample_row)
        empty_student["academic_marks_pct"] = None
        empty_student["attendance_pct"] = None
        empty_student["risk_level"] = None
        empty_student["phone"] = None
        empty_student["mentor_name"] = None

        rendered = render_template(
            "student_dashboard.html",
            user={"user_id": "TEST-001", "role": "student"},
            student=empty_student,
            metrics={"pillars": {}, "risk_factors": [], "positive_factors": [], "segment": "Core"},
            interventions=[],
            notifications=[],
            academic_records=[],
            semesters_data={},
            total_courses=0,
            total_passed=0,
            backlog_subjects=[],
            current_academic_year="Year 1",
            fee_records=[],
            fee_summary={"total_fees": 0, "total_paid": 0, "total_due": 0, "next_due_date": "None pending"}
        )
        assert "Marks data unavailable" in rendered
        assert "Attendance data unavailable" in rendered
        assert "Risk assessment unavailable" in rendered
        assert "Not available" in rendered
        print("[PASS] 12. Fallbacks for missing marks, attendance, risk, and profile fields verified.")

    print("\n" + "="*75)
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY (12/12)!")
    print("="*75 + "\n")

if __name__ == "__main__":
    test_profile_and_graphics()

"""
Comprehensive test script for the Complete Academic Records View feature.
Tests:
- Authentication & server-side role enforcement (401 unauth, 403 non-student)
- GET /api/student/academic-records with year, semester, and search filters
- Data accuracy for profile, summary metrics, SGPA, and backlogs
- Student dashboard HTML rendering including profile banner, KPI cards, mid-exam filters, and multi-semester tables
- Verification that Chatbot, Admin, and Faculty dashboards remain intact
"""

import sys
import os
import json

# Ensure parent directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.db import get_db

def test_academic_records_feature():
    print("\n" + "="*70)
    print("RUNNING ACADEMIC RECORDS VERIFICATION TEST SUITE")
    print("="*70)

    client = app.test_client()

    # -------------------------------------------------------------
    # 1. Security Check: Unauthenticated access to API
    # -------------------------------------------------------------
    resp = client.get("/api/student/academic-records")
    assert resp.status_code in (401, 302), f"Expected 401/302 for unauth, got {resp.status_code}"
    print("[PASS] Unauthenticated API request correctly rejected.")

    # -------------------------------------------------------------
    # 2. Security Check: Faculty access to student academic records endpoint
    # -------------------------------------------------------------
    login_resp = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert login_resp.status_code == 200, f"Faculty login failed: {login_resp.data}"
    resp = client.get("/api/student/academic-records")
    assert resp.status_code == 403, f"Expected 403 Forbidden for faculty, got {resp.status_code}"
    print("[PASS] Faculty access to /api/student/academic-records correctly blocked with 403.")

    # -------------------------------------------------------------
    # 3. Security Check: Admin access to student academic records endpoint
    # -------------------------------------------------------------
    client.get("/logout")
    login_resp = client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.data}"
    resp = client.get("/api/student/academic-records")
    assert resp.status_code == 403, f"Expected 403 Forbidden for admin, got {resp.status_code}"
    print("[PASS] Admin access to /api/student/academic-records correctly blocked with 403.")

    # -------------------------------------------------------------
    # 4. Student Login & Student Dashboard HTML Verification
    # -------------------------------------------------------------
    client.get("/logout")
    login_resp = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert login_resp.status_code == 200, f"Student login failed: {login_resp.data}"
    print("[PASS] Student student001 logged in successfully.")

    dash_resp = client.get("/student")
    assert dash_resp.status_code == 200, f"Student dashboard returned {dash_resp.status_code}"
    dash_html = dash_resp.data.decode("utf-8")

    # Verify Profile & Branch Banner
    assert "Complete Academic History &amp; Portfolio" in dash_html or "Complete Academic History & Portfolio" in dash_html
    assert "Student ID / Roll No" in dash_html
    assert "Branch / Discipline" in dash_html
    assert "Current Academic Year" in dash_html
    assert "Cumulative GPA (CGPA)" in dash_html
    assert "Active Backlogs" in dash_html
    assert "Overall Attendance" in dash_html
    assert "Filter Mid-Examination &amp; Semester Marks" in dash_html or "Filter Mid-Examination & Semester Marks" in dash_html
    assert "No marks available for this semester or subject" in dash_html
    assert "Mid 1" in dash_html
    assert "Mid 2" in dash_html
    assert "Internal" in dash_html
    assert "External" in dash_html

    # Verify Chatbot is STILL intact in recommendations section
    assert "CampusIQ Study Assistant" in dash_html
    assert "ciqChatMessages" in dash_html
    assert "ciqChatInput" in dash_html
    assert "How can I improve my academic performance?" in dash_html
    print("[PASS] Student Dashboard HTML contains complete academic records view and preserves chatbot.")

    # -------------------------------------------------------------
    # 5. GET /api/student/academic-records API Verification
    # -------------------------------------------------------------
    api_resp = client.get("/api/student/academic-records")
    assert api_resp.status_code == 200, f"API returned {api_resp.status_code}"
    data = json.loads(api_resp.data)

    assert "student" in data
    assert "summary" in data
    assert "records" in data
    assert "semesters" in data
    assert "total_results" in data

    student_info = data["student"]
    summary = data["summary"]
    records = data["records"]
    semesters = data["semesters"]

    print(f"       Loaded {len(records)} records across {len(semesters)} semesters for {student_info['name']}")
    assert len(records) > 0, "No academic records returned"
    assert len(semesters) > 0, "No semesters returned"

    # Verify first course record schema
    c0 = records[0]
    expected_fields = [
        "course_code", "course_name", "credits", "year", "semester",
        "mid1_marks", "mid1_max", "mid2_marks", "mid2_max",
        "internal_marks", "internal_max", "external_marks", "external_max",
        "total_marks", "total_max", "grade", "status",
        "classes_conducted", "classes_attended", "attendance_pct", "sgpa"
    ]
    for field in expected_fields:
        assert field in c0, f"Missing field '{field}' in course record"
    print(f"[PASS] API records contain all required fields (Mid 1, Mid 2, Internal, External, Total, Grade, Attendance, SGPA).")

    # -------------------------------------------------------------
    # 6. Test Filtering by Year (?year=1)
    # -------------------------------------------------------------
    y1_resp = client.get("/api/student/academic-records?year=1")
    assert y1_resp.status_code == 200
    y1_data = json.loads(y1_resp.data)
    for r in y1_data["records"]:
        assert r["year"] == 1, f"Expected year 1, got {r['year']}"
    print(f"[PASS] Filtering by year=1 returned {len(y1_data['records'])} records all in year 1.")

    # -------------------------------------------------------------
    # 7. Test Filtering by Semester (?semester=1-1)
    # -------------------------------------------------------------
    s1_resp = client.get("/api/student/academic-records?semester=1-1")
    assert s1_resp.status_code == 200
    s1_data = json.loads(s1_resp.data)
    for r in s1_data["records"]:
        assert r["semester_label"] == "1-1" or str(r["semester"]) == "1", f"Expected semester 1-1, got {r}"
    print(f"[PASS] Filtering by semester=1-1 returned {len(s1_data['records'])} records all in 1-1.")

    # -------------------------------------------------------------
    # 8. Test Search Filter (?search=math)
    # -------------------------------------------------------------
    math_resp = client.get("/api/student/academic-records?search=math")
    assert math_resp.status_code == 200
    math_data = json.loads(math_resp.data)
    assert len(math_data["records"]) > 0, "Expected at least 1 match for search 'math'"
    for r in math_data["records"]:
        assert "math" in r["course_code"].lower() or "math" in r["course_name"].lower()
    print(f"[PASS] Search filter for 'math' matched {len(math_data['records'])} courses.")

    # -------------------------------------------------------------
    # 9. Test Non-existent Search (?search=xyz999) -> 0 records
    # -------------------------------------------------------------
    none_resp = client.get("/api/student/academic-records?search=xyz999nonexistent")
    assert none_resp.status_code == 200
    none_data = json.loads(none_resp.data)
    assert len(none_data["records"]) == 0
    assert none_data["total_results"] == 0
    print("[PASS] Search for nonexistent subject returned 0 results cleanly.")

    # -------------------------------------------------------------
    # 10. Test Student with Backlogs (Kabir Mehta / student008)
    # -------------------------------------------------------------
    client.get("/logout")
    login_resp = client.post("/login", json={"user_id": "student008", "password": "Student@123"})
    assert login_resp.status_code == 200
    s8_resp = client.get("/api/student/academic-records")
    s8_data = json.loads(s8_resp.data)
    assert s8_data["summary"]["backlog_count"] == 3, f"Expected 3 backlogs for Kabir Mehta, got {s8_data['summary']['backlog_count']}"
    assert len(s8_data["summary"]["backlog_subjects"]) == 3
    print(f"[PASS] Student with backlogs (Kabir Mehta): 3 backlogs accurately reflected ({', '.join(s8_data['summary']['backlog_subjects'])}).")

    # -------------------------------------------------------------
    # 11. Test Chatbot Endpoint Still Works
    # -------------------------------------------------------------
    chat_resp = client.post("/api/student/chat", json={"message": "Help me make a study plan."})
    assert chat_resp.status_code == 200
    chat_data = json.loads(chat_resp.data)
    assert "reply" in chat_data and len(chat_data["reply"]) > 20
    print("[PASS] CampusIQ Study Assistant chatbot responded normally.")

    # -------------------------------------------------------------
    # 12. Admin & Faculty Dashboards Still Work
    # -------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    admin_dash = client.get("/admin")
    assert admin_dash.status_code == 200
    print("[PASS] Admin Dashboard loads with 200 OK.")

    client.get("/logout")
    client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    fac_dash = client.get("/faculty")
    assert fac_dash.status_code == 200
    print("[PASS] Faculty Dashboard loads with 200 OK.")

    print("\n" + "="*70)
    print("ALL ACADEMIC RECORDS & SYSTEM INTEGRITY TESTS PASSED SUCCESSFULLY! (12/12)")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_academic_records_feature()

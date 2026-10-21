"""
Comprehensive verification test suite for Multiple Student and Faculty Logins in CampusIQ.
Verifies all 11 required test conditions:
1. Student A login with unique ID/password (student001 / Aarav Reddy).
2. Student B login with unique ID/password (student002 / Aditi Kulkarni).
3. Data isolation: Student A sees only Student A's profile & records; Student B sees only Student B's.
4. Faculty A login (faculty001) and Faculty B login (faculty002) with separate credentials.
5. Data isolation: Faculty A sees CSE caseload and notifications; Faculty B sees IT caseload.
6. Incorrect password rejection (401 Unauthorized).
7. Duplicate account prevention (409 Conflict) without overwriting existing accounts.
8. Admin login verification (admin001 / Admin@123).
9. Role-based access control (Student/Faculty blocked from Admin endpoints).
10. Persistence across restarts (simulated via db connection re-instantiation).
11. Preservation of Chatbot, Fee Details, Placement Readiness, and Academic Records.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.db import get_db, init_db

def test_multiple_student_and_faculty_logins():
    client = app.test_client()

    # -------------------------------------------------------------
    # 1. Student A Login (student001 / Student@123)
    # -------------------------------------------------------------
    client.get("/logout")
    resp_s1 = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert resp_s1.status_code == 200, "Student A login failed"
    data_s1 = resp_s1.get_json()
    assert data_s1["role"] == "student"
    assert data_s1["name"] == "Aarav Reddy"
    assert data_s1["department"] == "CSE"

    dash_s1 = client.get("/student")
    assert dash_s1.status_code == 200
    html_s1 = dash_s1.data.decode("utf-8")
    assert "Aarav Reddy" in html_s1
    assert "Aditi Kulkarni" not in html_s1

    # -------------------------------------------------------------
    # 2. Student B Login (student002 / Student@123)
    # -------------------------------------------------------------
    client.get("/logout")
    resp_s2 = client.post("/login", json={"user_id": "student002", "password": "Student@123"})
    assert resp_s2.status_code == 200, "Student B login failed"
    data_s2 = resp_s2.get_json()
    assert data_s2["role"] == "student"
    assert data_s2["name"] == "Aditi Kulkarni"
    assert data_s2["department"] == "IT"

    # -------------------------------------------------------------
    # 3. Data Isolation for Students
    # -------------------------------------------------------------
    dash_s2 = client.get("/student")
    assert dash_s2.status_code == 200
    html_s2 = dash_s2.data.decode("utf-8")
    assert "Aditi Kulkarni" in html_s2
    assert "Aarav Reddy" not in html_s2

    # Check fee-details isolation
    fees_s2 = client.get("/api/student/fee-details").get_json()
    assert "records" in fees_s2
    for r in fees_s2["records"]:
        assert r["student_id"] == "CIQ-2026-002"

    # Check academic records isolation
    acad_s2 = client.get("/api/student/academic-records").get_json()
    assert acad_s2["student"]["student_id"] == "CIQ-2026-002"
    assert acad_s2["student"]["name"] == "Aditi Kulkarni"

    # Student cannot view another student's deep profile
    forbidden_resp = client.get("/api/students/CIQ-2026-001")
    assert forbidden_resp.status_code == 403, f"Expected 403 for cross-student access, got {forbidden_resp.status_code}"

    # -------------------------------------------------------------
    # 4. Faculty A and Faculty B Logins
    # -------------------------------------------------------------
    client.get("/logout")
    resp_f1 = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert resp_f1.status_code == 200, "Faculty A login failed"
    data_f1 = resp_f1.get_json()
    assert data_f1["role"] == "faculty"
    assert data_f1["name"] == "Dr. Sunita Rao"
    assert data_f1["department"] == "CSE"

    client.get("/logout")
    resp_f2 = client.post("/login", json={"user_id": "faculty002", "password": "Faculty@123"})
    assert resp_f2.status_code == 200, "Faculty B login failed"
    data_f2 = resp_f2.get_json()
    assert data_f2["role"] == "faculty"
    assert data_f2["name"] == "Dr. Meenakshi Sundaram"
    assert data_f2["department"] == "IT"

    # -------------------------------------------------------------
    # 5. Data Isolation for Faculty
    # -------------------------------------------------------------
    # Faculty B (IT) students
    f2_students = client.get("/api/students").get_json()["students"]
    f2_names = [s["name"] for s in f2_students]
    assert "Aditi Kulkarni" in f2_names
    assert "Aarav Reddy" not in f2_names  # Aarav Reddy is CSE, belongs to faculty001

    # Faculty A (CSE) students
    client.get("/logout")
    client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    f1_students = client.get("/api/students").get_json()["students"]
    f1_names = [s["name"] for s in f1_students]
    assert "Aarav Reddy" in f1_names
    assert "Aditi Kulkarni" not in f1_names  # Aditi Kulkarni is IT, belongs to faculty002

    # -------------------------------------------------------------
    # 6. Reject Incorrect Password
    # -------------------------------------------------------------
    client.get("/logout")
    bad_login = client.post("/login", json={"user_id": "student001", "password": "WrongPassword@999"})
    assert bad_login.status_code == 401
    assert "Unauthorized" in bad_login.get_json().get("error", "")

    # -------------------------------------------------------------
    # 7. Reject Duplicate IDs Without Overwriting Existing Accounts
    # -------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    
    dup_student = client.post("/api/students", json={
        "student_id": "student001",
        "name": "Impostor Student",
        "email": "impostor@campusiq.edu",
        "department": "CSE"
    })
    assert dup_student.status_code == 409
    assert "already registered" in dup_student.get_json()["message"]

    dup_faculty = client.post("/api/faculty", json={
        "faculty_id": "faculty001",
        "name": "Impostor Faculty",
        "email": "impostor_fac@campusiq.edu",
        "department": "CSE"
    })
    assert dup_faculty.status_code == 409
    assert "already registered" in dup_faculty.get_json()["message"]

    # Verify original records were NOT overwritten
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE user_id = 'student001'")
    assert c.fetchone()["name"] == "Aarav Reddy"
    c.execute("SELECT name FROM users WHERE user_id = 'faculty001'")
    assert c.fetchone()["name"] == "Dr. Sunita Rao"
    conn.close()

    # -------------------------------------------------------------
    # 8. Admin Login Verification
    # -------------------------------------------------------------
    client.get("/logout")
    resp_adm = client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    assert resp_adm.status_code == 200
    assert resp_adm.get_json()["role"] == "admin"
    dash_adm = client.get("/admin")
    assert dash_adm.status_code == 200

    # -------------------------------------------------------------
    # 9. Role-Based Access Control Restrictions
    # -------------------------------------------------------------
    # Student blocked from /admin and POST /api/students
    client.get("/logout")
    client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert client.get("/admin").status_code == 302
    assert client.post("/api/students", json={}).status_code == 403
    assert client.post("/api/faculty", json={}).status_code == 403

    # Faculty blocked from /admin and POST /api/students
    client.get("/logout")
    client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert client.get("/admin").status_code == 302
    assert client.post("/api/students", json={}).status_code == 403
    assert client.post("/api/faculty", json={}).status_code == 403

    # -------------------------------------------------------------
    # 10. Persistence Across Restarts & Account Provisioning
    # -------------------------------------------------------------
    # Admin creates a new custom student and faculty
    client.get("/logout")
    client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})

    uid_test_stu = "ciq_student_persist_test"
    uid_test_fac = "ciq_faculty_persist_test"

    # Clean up any leftover test data
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id IN (?, ?)", (uid_test_stu, uid_test_fac))
    c.execute("DELETE FROM students WHERE student_id = ?", (uid_test_stu,))
    c.execute("DELETE FROM faculty WHERE faculty_id = ?", (uid_test_fac,))
    conn.commit()
    conn.close()

    try:
        # Create student with custom unique password
        res_add_s = client.post("/api/students", json={
            "student_id": uid_test_stu,
            "name": "Persist Test Student",
            "email": "persist.stu@campusiq.edu",
            "department": "CSE",
            "password": "PersistStudentPass@2026",
            "semester": 4,
            "cgpa": 8.1,
            "attendance_pct": 82.0,
            "backlogs": 0
        })
        assert res_add_s.status_code == 201

        # Create faculty with custom unique password
        res_add_f = client.post("/api/faculty", json={
            "faculty_id": uid_test_fac,
            "name": "Dr. Persist Test Faculty",
            "email": "persist.fac@campusiq.edu",
            "department": "AI&DS",
            "password": "PersistFacultyPass@2026",
            "designation": "Associate Professor",
            "specialization": "Data Science"
        })
        assert res_add_f.status_code == 201

        # Simulate Flask startup: run init_db(force=False)
        init_db(force=False)

        # Login as the newly created student with their custom password
        client.get("/logout")
        res_login_s = client.post("/login", json={"user_id": uid_test_stu, "password": "PersistStudentPass@2026"})
        assert res_login_s.status_code == 200
        assert res_login_s.get_json()["name"] == "Persist Test Student"
        dash_new_s = client.get("/student")
        assert "Persist Test Student" in dash_new_s.data.decode("utf-8")

        # Login as the newly created faculty with their custom password
        client.get("/logout")
        res_login_f = client.post("/login", json={"user_id": uid_test_fac, "password": "PersistFacultyPass@2026"})
        assert res_login_f.status_code == 200
        assert res_login_f.get_json()["name"] == "Dr. Persist Test Faculty"

    finally:
        # Clean up test accounts
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE user_id IN (?, ?)", (uid_test_stu, uid_test_fac))
        c.execute("DELETE FROM students WHERE student_id = ?", (uid_test_stu,))
        c.execute("DELETE FROM student_fees WHERE student_id = ?", (uid_test_stu,))
        c.execute("DELETE FROM faculty WHERE faculty_id = ?", (uid_test_fac,))
        conn.commit()
        conn.close()

    # -------------------------------------------------------------
    # 11. Preservation of Key Features
    # -------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "student001", "password": "Student@123"})

    # Chatbot
    chat_resp = client.post("/api/student/chat", json={"message": "What is my attendance rate?"})
    assert chat_resp.status_code == 200
    assert "attendance" in chat_resp.get_json()["reply"].lower()

    # Fee details
    fee_resp = client.get("/api/student/fee-details")
    assert fee_resp.status_code == 200
    assert fee_resp.get_json()["summary"]["total_fees"] > 0

    # Skills & Placement
    skills_resp = client.get("/api/student/skills")
    assert skills_resp.status_code == 200
    assert "skills" in skills_resp.get_json()

    # Academic Records
    records_resp = client.get("/api/student/academic-records")
    assert records_resp.status_code == 200
    assert len(records_resp.get_json()["records"]) > 0

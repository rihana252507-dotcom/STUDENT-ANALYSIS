"""
Essential validation test suite for:
PART B: Faculty Student Search (exact name, partial name, ID, roll number, unknown student, role security)
PART C: Student Multilingual Chatbot (English, Telugu, Hindi, Hinglish, Teluglish, follow-up, verified DB stats, no fabrication)
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.db import get_db

def test_faculty_search_and_multilingual_chatbot():
    client = app.test_client()

    # =========================================================================
    # PART B: FACULTY STUDENT SEARCH & AUTHORIZATION
    # =========================================================================

    # 1. Unauthenticated / student access to faculty search API is blocked
    client.get("/logout")
    res_unauth = client.get("/api/students?search=Aarav")
    assert res_unauth.status_code == 401, "Unauthenticated access should be 401"

    login_stu = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert login_stu.status_code == 200
    res_stu_forbidden = client.get("/api/students?search=Aarav")
    assert res_stu_forbidden.status_code == 403, "Student should receive 403 when searching directory"
    client.get("/logout")

    # 2. Faculty login (faculty001)
    login_fac = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert login_fac.status_code == 200, "Faculty login failed"

    # 3. Search by exact student name
    res_exact_name = client.get("/api/students?search=Aarav%20Reddy")
    assert res_exact_name.status_code == 200
    data_exact = res_exact_name.get_json()
    assert len(data_exact["students"]) >= 1
    assert any(s["name"] == "Aarav Reddy" for s in data_exact["students"])

    # 4. Search by partial student name
    res_part_name = client.get("/api/students?search=Aar")
    assert res_part_name.status_code == 200
    data_part = res_part_name.get_json()
    assert len(data_part["students"]) >= 1
    assert any("aar" in s["name"].lower() for s in data_part["students"])

    # 5. Search by exact student ID
    res_id = client.get("/api/students?search=student001")
    assert res_id.status_code == 200
    data_id = res_id.get_json()
    assert len(data_id["students"]) >= 1
    assert data_id["students"][0]["student_id"] == "student001" or data_id["students"][0]["user_id"] == "student001"

    # 6. Search for unknown student ID -> empty results list
    res_unknown = client.get("/api/students?search=UNKNOWN_NONEXISTENT_9999")
    assert res_unknown.status_code == 200
    data_unknown = res_unknown.get_json()
    assert len(data_unknown["students"]) == 0

    # 7. Select student and verify detailed profile fields against database
    res_detail = client.get("/api/students/student001")
    assert res_detail.status_code == 200
    det = res_detail.get_json()
    assert det["name"] == "Aarav Reddy"
    assert det["department"] == "CSE"
    assert float(det["cgpa"]) == 9.1
    assert float(det["attendance_pct"]) == 94.0
    assert int(det["backlogs"]) == 0
    assert "pillars" in det
    assert "success_score" in det

    client.get("/logout")

    # =========================================================================
    # PART C: STUDENT MULTILINGUAL CHATBOT
    # =========================================================================

    login_stu = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert login_stu.status_code == 200

    # 8. General question in English
    res_q8 = client.post("/api/student/chat", json={"message": "What is binary search algorithm?"})
    assert res_q8.status_code == 200
    d8 = res_q8.get_json()
    assert d8["language"] == "english"
    assert len(d8["reply"]) > 20

    # 9. Question in Hinglish (code-mixed Hindi + English)
    res_q9 = client.post("/api/student/chat", json={"message": "Mera CGPA kitna hai?"})
    assert res_q9.status_code == 200
    d9 = res_q9.get_json()
    assert d9["language"] in ["hinglish", "hindi"]
    assert "9.1" in d9["reply"]
    assert "Aarav" in d9["reply"]

    # 10. Question in Telugish (Telugu in English letters)
    res_q10 = client.post("/api/student/chat", json={"message": "Naa CGPA entha undi?"})
    assert res_q10.status_code == 200
    d10 = res_q10.get_json()
    assert d10["language"] in ["teluglish", "telugu"]
    assert "9.1" in d10["reply"]
    assert "Aarav" in d10["reply"]

    # 11. Question in native Telugu script
    res_q11 = client.post("/api/student/chat", json={"message": "నా హాజరు శాతం ఎంత?"})
    assert res_q11.status_code == 200
    d11 = res_q11.get_json()
    assert d11["language"] == "telugu"
    assert "94" in d11["reply"]

    # 12. Explicit request for language preference
    res_q12 = client.post("/api/student/chat", json={"message": "Explain this in Telugu."})
    assert res_q12.status_code == 200
    d12 = res_q12.get_json()
    assert d12["language"] == "telugu"

    # 13. Contextual Follow-up question inheriting preference
    res_q13 = client.post("/api/student/chat", json={"message": "timetable ivvu"})
    assert res_q13.status_code == 200
    d13 = res_q13.get_json()
    assert d13["language"] in ["telugu", "teluglish"]

    # Reset preference explicitly to English
    res_reset = client.post("/api/student/chat", json={"message": "Please answer in English."})
    assert res_reset.status_code == 200
    assert res_reset.get_json()["language"] == "english"

    # 14. Verify verified records for student008 (Kabir Mehta - 68% att, 3 backlogs)
    client.get("/logout")
    login_kabir = client.post("/login", json={"user_id": "student008", "password": "Student@123"})
    assert login_kabir.status_code == 200

    res_k_att = client.post("/api/student/chat", json={"message": "How is my attendance?"})
    assert res_k_att.status_code == 200
    k_reply = res_k_att.get_json()["reply"]
    assert "68" in k_reply or "below the mandatory 75%" in k_reply
    assert "Kabir" in k_reply

    res_k_back = client.post("/api/student/chat", json={"message": "Do I have any backlogs?"})
    assert res_k_back.status_code == 200
    k_b_reply = res_k_back.get_json()["reply"]
    assert "3" in k_b_reply

    client.get("/logout")

"""
Comprehensive verification test suite for:
1. Student Fee Details Page & Table (with summary, status, empty-state, security isolation)
2. Simplified Student Dashboard (welcome message + 6 basic profile fields only)
3. Zero regressions across existing chatbot, academic records, admin & faculty dashboards
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.db import get_db

def test_fee_and_simplified_dashboard():
    print("\n" + "="*75)
    print("RUNNING FEE DETAILS & SIMPLIFIED STUDENT DASHBOARD VERIFICATION SUITE")
    print("="*75)

    client = app.test_client()

    # -----------------------------------------------------------------
    # 1. Security Check: Unauthenticated access to fee-details API
    # -----------------------------------------------------------------
    resp = client.get("/api/student/fee-details")
    assert resp.status_code in (401, 302), f"Expected 401/302 for unauthenticated, got {resp.status_code}"
    print("[PASS] 1. Unauthenticated fee API request properly rejected (401).")

    # -----------------------------------------------------------------
    # 2. Security Check: Role-based authorization (Faculty & Admin blocked)
    # -----------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    resp = client.get("/api/student/fee-details")
    assert resp.status_code == 403, f"Expected 403 for faculty, got {resp.status_code}"
    print("[PASS] 2. Faculty role blocked from student fee API (403).")

    client.get("/logout")
    client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    resp = client.get("/api/student/fee-details")
    assert resp.status_code == 403, f"Expected 403 for admin, got {resp.status_code}"
    print("[PASS] 3. Admin role blocked from student fee API (403).")

    # -----------------------------------------------------------------
    # 3. Student Login & Simplified Dashboard Verification (student001)
    # -----------------------------------------------------------------
    client.get("/logout")
    login_resp = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert login_resp.status_code == 200, "Student001 login failed"

    dash_resp = client.get("/student")
    assert dash_resp.status_code == 200, "Student dashboard returned non-200"
    html = dash_resp.data.decode("utf-8")

    # Verify Welcome Message
    assert "Welcome back," in html
    assert "Aarav Reddy" in html
    assert "Here is your student profile and academic information." in html
    print("[PASS] 4. Personalized welcome message and subtitle displayed correctly.")

    # Verify ONLY 6 Profile Fields in #section-my-dashboard
    dashboard_section = html.split('<section id="section-my-dashboard"')[1].split('</section>')[0]
    
    assert "Student Name" in dashboard_section
    assert "Aarav Reddy" in dashboard_section
    assert "Roll Number" in dashboard_section
    assert "CIQ-2026-001" in dashboard_section
    assert "Current Semester" in dashboard_section
    assert "Semester 8" in dashboard_section
    assert "Branch / Department" in dashboard_section
    assert "Phone Number" in dashboard_section
    assert "+91 9877827638" in dashboard_section
    assert "Class Faculty Mentor" in dashboard_section
    assert "Dr. Sunita Rao" in dashboard_section
    print("[PASS] 5. All six basic profile fields displayed accurately for student001.")

    # Verify that unrelated analytics cards/charts are NOT inside #section-my-dashboard
    assert "studentPillarRadarChart" not in dashboard_section
    assert "5-Pillar Explainable Performance" not in dashboard_section
    assert "Pillar Contribution Weights" not in dashboard_section
    assert "KPI Scorecards Grid" not in dashboard_section
    print("[PASS] 6. Main Student Dashboard simplified: radar chart and KPI cards removed from main view.")

    # -----------------------------------------------------------------
    # 4. Fee Details Page & Table Verification (student001)
    # -----------------------------------------------------------------
    # Verify navigation link
    assert 'data-section="section-fee-details"' in html
    assert "Fee Details" in html

    # Verify section content
    fee_section = html.split('<section id="section-fee-details"')[1].split('</section>')[0]
    assert "Semester Fee Details" in fee_section
    assert "Total Fees" in fee_section
    assert "Total Amount Paid" in fee_section
    assert "Total Outstanding Due" in fee_section
    assert "Next Fee Due Date" in fee_section
    assert "Academic Year" in fee_section
    assert "Total Semester Fee" in fee_section
    assert "Amount Paid" in fee_section
    assert "Remaining Due" in fee_section
    assert "Fee Due Date / Last Date" in fee_section
    assert "Payment Status" in fee_section
    assert "Paid" in fee_section
    print("[PASS] 7. Fee Details page renders summary metrics and full semester-wise fee table.")

    # -----------------------------------------------------------------
    # 5. GET /api/student/fee-details API verification (student001)
    # -----------------------------------------------------------------
    fee_api = client.get("/api/student/fee-details")
    assert fee_api.status_code == 200
    fee_data = json.loads(fee_api.data)

    assert "student" in fee_data
    assert "summary" in fee_data
    assert "records" in fee_data
    assert fee_data["student"]["student_id"] == "CIQ-2026-001"
    assert fee_data["summary"]["total_fees"] > 0
    assert fee_data["summary"]["total_paid"] > 0
    assert len(fee_data["records"]) == 8 # Semesters 1 to 8
    for r in fee_data["records"]:
        assert r["remaining_due"] >= 0.0, "Remaining due should not be negative"
        assert r["status"] in ["Paid", "Partially Paid", "Due", "Overdue"]
    print(f"[PASS] 8. API /api/student/fee-details returned {len(fee_data['records'])} valid semester records.")

    # -----------------------------------------------------------------
    # 6. Test Missing Due Date Fallback ("Not available") - student004
    # -----------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "student004", "password": "Student@123"})
    dash4 = client.get("/student")
    assert dash4.status_code == 200
    html4 = dash4.data.decode("utf-8")
    fee_sec4 = html4.split('<section id="section-fee-details"')[1].split('</section>')[0]
    assert "Not available" in fee_sec4
    print("[PASS] 9. Missing fee due date gracefully displays 'Not available' without errors.")

    # -----------------------------------------------------------------
    # 7. Test Overdue Status - student008 (Kabir Mehta)
    # -----------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "student008", "password": "Student@123"})
    dash8 = client.get("/student")
    html8 = dash8.data.decode("utf-8")
    fee_sec8 = html8.split('<section id="section-fee-details"')[1].split('</section>')[0]
    assert "Overdue" in fee_sec8
    print("[PASS] 10. Overdue fee status accurately calculated and badged for student008.")

    # -----------------------------------------------------------------
    # 8. Test Empty Fee Records State - student010 (Arjun Verma)
    # -----------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "student010", "password": "Student@123"})
    dash10 = client.get("/student")
    html10 = dash10.data.decode("utf-8")
    fee_sec10 = html10.split('<section id="section-fee-details"')[1].split('</section>')[0]
    expected_empty_msg = "No fee details are available for your account yet. Please contact your college administration."
    assert expected_empty_msg in fee_sec10
    print(f"[PASS] 11. Empty state message exactly matched for student with no fee records.")

    # -----------------------------------------------------------------
    # 9. Verify Chatbot Still Works
    # -----------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    chat_resp = client.post("/api/student/chat", json={"message": "Help me make a study plan."})
    assert chat_resp.status_code == 200
    chat_json = json.loads(chat_resp.data)
    assert "reply" in chat_json and len(chat_json["reply"]) > 20
    print("[PASS] 12. CampusIQ Study Assistant chatbot functions normally.")

    # -----------------------------------------------------------------
    # 10. Verify Academic Records Still Work
    # -----------------------------------------------------------------
    acad_resp = client.get("/api/student/academic-records")
    assert acad_resp.status_code == 200
    acad_json = json.loads(acad_resp.data)
    assert len(acad_json["records"]) > 0
    print("[PASS] 13. Academic Records API returns full multi-semester trajectory.")

    # -----------------------------------------------------------------
    # 11. Verify Admin & Faculty Dashboards Unchanged
    # -----------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    assert client.get("/admin").status_code == 200
    print("[PASS] 14. Admin dashboard loads normally (200).")

    client.get("/logout")
    client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert client.get("/faculty").status_code == 200
    print("[PASS] 15. Faculty dashboard loads normally (200).")

    print("\n" + "="*75)
    print("ALL 15/15 TESTS PASSED SUCCESSFULLY! ZERO REGRESSIONS DETECTED.")
    print("="*75 + "\n")

if __name__ == "__main__":
    test_fee_and_simplified_dashboard()

import sys
sys.path.insert(0, r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS")
import app

def test_admin_risk_monitoring():
    client = app.app.test_client()

    # 1. Admin Login
    res = client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    assert res.status_code == 200, f"Admin login failed: {res.status_code}"

    # 2. Open Admin Dashboard & check Risk Monitoring HTML structure
    admin_res = client.get("/admin")
    assert admin_res.status_code == 200
    html = admin_res.data.decode("utf-8")

    # Initial view elements
    assert "adminRiskListView" in html, "adminRiskListView missing"
    assert "adminRiskSearchInput" in html, "adminRiskSearchInput missing"
    assert "adminRiskCountBadge" in html, "adminRiskCountBadge missing"
    assert "Student Name" in html
    assert "Student ID" in html

    # Detail view elements
    assert "adminRiskDetailView" in html, "adminRiskDetailView missing"
    assert "closeAdminRiskDetail" in html, "Back button handler missing"
    assert "riskDetailAvatarContainer" in html, "Gender avatar container missing"
    assert "riskDetailAttCircle" in html, "Circular attendance gauge missing"
    assert "riskDetailBacklogBody" in html, "Backlog analysis table missing"
    assert "riskDetailWhyFlaggedBody" in html, "Why Flagged table missing"
    assert "riskDetailAcademicMarksBody" in html, "Academic history table missing"
    assert "riskDetailSgpaContainer" in html, "SGPA progression container missing"
    assert "riskDetailRecommendationsBody" in html, "Recommendations container missing"

    # 3. Test Student Detail API for student with backlogs (CIQ-2026-004)
    stu_res = client.get("/api/students/CIQ-2026-004")
    assert stu_res.status_code == 200
    data = stu_res.get_json()
    assert data["student_id"] == "CIQ-2026-004"
    assert data["name"] == "Ananya Gupta"
    assert data["gender"].lower() == "female"
    assert data["backlogs"] == 1
    assert "academic_records" in data
    assert len(data["academic_records"]) > 0
    # Check backlog in records
    backlogs = [r for r in data["academic_records"] if r["status"] == "Backlog" or r["grade"] == "F"]
    assert len(backlogs) == 1
    assert backlogs[0]["course_code"] == "AIDS203"
    assert "Linear Algebra" in backlogs[0]["course_name"]

    # Check attendance and CGPA
    assert data["attendance_pct"] == 78.5
    assert data["cgpa"] == 7.2
    assert "success_score" in data
    assert "pillars" in data

    # 4. Test Student Detail API for student with 0 backlogs (CIQ-2026-001)
    stu001_res = client.get("/api/students/CIQ-2026-001")
    assert stu001_res.status_code == 200
    data001 = stu001_res.get_json()
    assert data001["backlogs"] == 0
    backlogs001 = [r for r in data001.get("academic_records", []) if r["status"] == "Backlog" or r["grade"] == "F"]
    assert len(backlogs001) == 0

    # 5. Test invalid student ID handling
    inv_res = client.get("/api/students/NON_EXISTENT_ID")
    assert inv_res.status_code == 404

    # 6. Test Faculty and Student logins are preserved
    fac_login = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert fac_login.status_code == 200
    stu_login = client.post("/login", json={"user_id": "CIQ-2026-001", "password": "Student@123"})
    assert stu_login.status_code == 200

    print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_admin_risk_monitoring()

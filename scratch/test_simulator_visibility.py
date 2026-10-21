import sys
sys.path.insert(0, r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS")
import app

def test_simulator_visibility_and_functionality():
    client = app.app.test_client()

    # 1. Admin login & HTML checks
    res = client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    assert res.status_code == 200

    admin_res = client.get("/admin")
    assert admin_res.status_code == 200
    admin_html = admin_res.data.decode("utf-8")

    # Check simulator modal in admin
    assert 'id="simulatorModal"' in admin_html
    assert 'CampusIQ What-If Academic Simulator' in admin_html
    # Ensure header does not use unreadable white text on white
    assert 'color:#FFFFFF; font-size:1.25rem; font-weight:800;">CampusIQ What-If Academic Simulator' not in admin_html
    assert 'color:#111827; font-size:1.25rem; font-weight:800;' in admin_html
    # Ensure delta highlight in simulator modal is high contrast
    sim_modal_html = admin_html[admin_html.find('id="simulatorModal"'):]
    assert 'color:#6EE7B7' not in sim_modal_html  # Was pale neon green in modal
    assert 'color:#065F46' in sim_modal_html      # Dark high-contrast green

    # 2. Test Simulation Backend API for Admin
    sim_payload = {
        "student_id": "CIQ-2026-004",
        "attendance_boost": 10,
        "clear_backlogs": 1,
        "lms_hours_boost": 5,
        "assignment_boost": 15
    }
    sim_res = client.post("/api/simulate", json=sim_payload)
    assert sim_res.status_code == 200
    sim_data = sim_res.get_json()
    assert "simulated" in sim_data
    assert "score_delta" in sim_data
    assert sim_data["simulated"]["success_score"] > 0
    print(f"Admin simulation passed: Original {sim_data['original']['success_score']} -> Simulated {sim_data['simulated']['success_score']} (+{sim_data['score_delta']} pts)")

    # 3. Faculty login & HTML checks
    fac_login = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert fac_login.status_code == 200

    fac_res = client.get("/faculty")
    assert fac_res.status_code == 200
    fac_html = fac_res.data.decode("utf-8")
    assert 'id="simulatorModal"' in fac_html
    assert 'color:#FFFFFF; font-size:1.25rem; font-weight:800;">CampusIQ What-If Academic Simulator' not in fac_html
    assert 'color:#111827; font-size:1.25rem; font-weight:800;' in fac_html

    # 4. Student login & HTML checks
    stu_login = client.post("/login", json={"user_id": "CIQ-2026-001", "password": "Student@123"})
    assert stu_login.status_code == 200

    stu_res = client.get("/student")
    assert stu_res.status_code == 200
    stu_html = stu_res.data.decode("utf-8")

    # Check student simulator section
    assert 'id="section-my-success-score"' in stu_html
    assert 'Interactive What-If Simulator' in stu_html
    # Ensure no faint lavender text on white card
    assert 'color:#E9D5FF; line-height:1.6;' not in stu_html
    # Ensure projected score is NOT white text on white/light background
    assert 'id="personalProjectedScore" style="font-size:1.6rem; font-weight:800; color:#FFFFFF;"' not in stu_html
    assert 'id="personalProjectedScore" style="font-size:1.6rem; font-weight:800; color:#111827;"' in stu_html

    # 5. Test Simulation Backend API for Student
    stu_sim_res = client.post("/api/simulate", json={
        "student_id": "CIQ-2026-001",
        "attendance_boost": 5,
        "clear_backlogs": 0,
        "lms_hours_boost": 3,
        "assignment_boost": 10
    })
    assert stu_sim_res.status_code == 200
    stu_sim_data = stu_sim_res.get_json()
    assert "simulated" in stu_sim_data
    assert "score_delta" in stu_sim_data
    print(f"Student simulation passed: Original {stu_sim_data['original']['success_score']} -> Simulated {stu_sim_data['simulated']['success_score']} (+{stu_sim_data['score_delta']} pts)")

    print("\nALL SIMULATOR VISIBILITY & FUNCTIONALITY TESTS PASSED!")

if __name__ == "__main__":
    test_simulator_visibility_and_functionality()

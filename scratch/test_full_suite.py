from database.db import get_db
from services.analytics import analytics_engine
from app import app

def test_everything():
    print("=== Testing CampusIQ Hackathon Prototype ===")
    
    # 1. Check Database Counts
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    faculty = conn.execute("SELECT * FROM faculty").fetchall()
    courses = conn.execute("SELECT * FROM courses").fetchall()
    interventions = conn.execute("SELECT * FROM interventions").fetchall()
    conn.close()

    print(f"Total students in DB: {len(students)}")
    assert len(students) == 10, f"Expected 10 students, got {len(students)}"
    print(f"Total faculty in DB: {len(faculty)}")
    assert len(faculty) >= 5, "Expected at least 5 faculty"
    print(f"Total courses in DB: {len(courses)}")
    print(f"Total interventions in DB: {len(interventions)}")

    # 2. Check Risk Distribution
    risk_counts = {"Low": 0, "Medium": 0, "High": 0}
    for s in students:
        s_dict = dict(s)
        metrics = analytics_engine.compute_student_metrics(s_dict)
        risk = metrics["risk_level"]
        risk_counts[risk] += 1
        print(f"  {s['student_id']}: {s['name']} -> Score {metrics['success_score']}, Risk {risk}, Attendance {s['attendance_pct']}%, Backlogs {s['backlogs']}")

    print(f"Risk Counts: {risk_counts}")
    assert risk_counts["Low"] == 2, f"Expected 2 Low, got {risk_counts['Low']}"
    assert risk_counts["Medium"] == 4, f"Expected 4 Medium, got {risk_counts['Medium']}"
    assert risk_counts["High"] == 4, f"Expected 4 High, got {risk_counts['High']}"

    # 3. Test Flask Test Client & Authentication
    client = app.test_client()
    
    # Admin Login
    res_admin = client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    assert res_admin.status_code == 200, f"Admin login failed: {res_admin.data}"
    admin_data = res_admin.get_json()
    assert admin_data["role"] == "admin"
    print("Admin login: OK")

    # Faculty Login
    res_faculty = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert res_faculty.status_code == 200, f"Faculty login failed: {res_faculty.data}"
    fac_data = res_faculty.get_json()
    assert fac_data["role"] == "faculty"
    print("Faculty login: OK")

    # Student Login
    res_student = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert res_student.status_code == 200, f"Student login failed: {res_student.data}"
    stu_data = res_student.get_json()
    assert stu_data["role"] == "student"
    print("Student login: OK")

    # 4. Role Authorization & Student Isolation
    with client.session_transaction() as sess:
        sess['user_id'] = 'student001'
        sess['role'] = 'student'
        sess['name'] = 'Aarav Reddy'
        sess['student_id'] = 'CIQ-2026-001'

    # Student accessing own profile -> should succeed
    res_own = client.get("/api/students/CIQ-2026-001")
    assert res_own.status_code == 200, "Student accessing own profile should return 200"
    print("Student self-access: OK")

    # Student accessing other student profile -> should be forbidden (403)
    res_other = client.get("/api/students/CIQ-2026-002")
    assert res_other.status_code == 403, f"Student accessing CIQ-2026-002 should be 403, got {res_other.status_code}"
    print("Student role privacy boundary (403 on other student): OK")

    # 5. Admin API Endpoints
    with client.session_transaction() as sess:
        sess['user_id'] = 'admin001'
        sess['role'] = 'admin'
        sess['name'] = 'Dr. Rajesh Sundaram'

    res_overview = client.get("/api/admin/overview")
    assert res_overview.status_code == 200
    ov_data = res_overview.get_json()
    assert ov_data["total_students"] == 10
    assert ov_data["risk_counts"]["high"] == 4
    assert ov_data["risk_counts"]["medium"] == 4
    assert ov_data["risk_counts"]["low"] == 2
    print(f"Admin Overview: total_students={ov_data['total_students']}, risk={ov_data['risk_counts']} - OK")

    res_charts = client.get("/api/admin/charts")
    assert res_charts.status_code == 200
    chart_data = res_charts.get_json()
    assert "risk_breakdown" in chart_data
    assert "department_chart" in chart_data
    assert "scatter_data" in chart_data
    print("Admin Charts API: OK")

    # 6. What-If Simulator API
    res_sim = client.post("/api/simulate", json={
        "student_id": "CIQ-2026-008",
        "attendance_boost": 20.0,
        "clear_backlogs": 2,
        "assignment_boost": 20.0
    })
    assert res_sim.status_code == 200
    sim_data = res_sim.get_json()
    print(f"What-If Simulation on CIQ-2026-008: Baseline {sim_data['original']['success_score']} ({sim_data['original']['risk_level']}) -> Simulated {sim_data['simulated']['success_score']} ({sim_data['simulated']['risk_level']}) Delta {sim_data['score_delta']} - OK")

    # 7. Intervention Status Update in SQLite
    res_intv = client.put("/api/interventions/1", json={"status": "Completed"})
    assert res_intv.status_code == 200
    # verify persistence
    conn = get_db()
    row = conn.execute("SELECT status FROM interventions WHERE id = 1").fetchone()
    conn.close()
    assert row["status"] == "Completed", f"Expected Completed, got {row['status']}"
    print("Intervention update & SQLite persistence: OK")

    # Reset back to In Progress for demo consistency
    conn = get_db()
    conn.execute("UPDATE interventions SET status = 'In Progress' WHERE id = 1")
    conn.commit()
    conn.close()

    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_everything()

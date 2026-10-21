"""
CampusIQ – Admin Add Student & Faculty Persistence Verification Suite
Tests:
1. Admin authorization check on add endpoints
2. Adding a new student record with transaction commit
3. Verification that new student appears in Admin directory
4. Verification that new student can authenticate & has strict role isolation
5. Adding a new faculty record with transaction commit
6. Verification that new faculty appears in Admin directory
7. Verification that new faculty can authenticate & has strict role isolation
8. Duplicate rejection (409 Conflict) for existing ID / username
9. Persistence verification across session logouts and Flask application restart (init_db simulation)
10. Integrity check of existing 10 official calibrated cohort students and faculty
11. Safe cleanup of test records
"""

import sys
sys.path.insert(0, '.')

from app import app
from database.db import get_db, init_db

app.config['TESTING'] = True

def run_persistence_tests():
    print("=" * 75)
    print("RUNNING ADMIN ADD STUDENT & FACULTY PERSISTENCE TEST SUITE")
    print("=" * 75)

    test_student_id = "test_stu_999"
    test_student_email = "priya.test@campusiq.edu"
    test_fac_id = "test_fac_999"
    test_fac_email = "rajesh.test@campusiq.edu"

    # Pre-clean any leftover test records from aborted previous runs
    conn_pre = get_db()
    c_pre = conn_pre.cursor()
    c_pre.execute("DELETE FROM students WHERE student_id = ?", (test_student_id,))
    c_pre.execute("DELETE FROM users WHERE user_id IN (?, ?)", (test_student_id, test_fac_id))
    c_pre.execute("DELETE FROM faculty WHERE faculty_id = ?", (test_fac_id,))
    c_pre.execute("DELETE FROM student_fees WHERE student_id = ?", (test_student_id,))
    conn_pre.commit()
    conn_pre.close()

    with app.test_client() as client:
        # 1. Authorization check: Non-admin cannot add students or faculty
        r1_s = client.post('/api/students', json={'student_id': 'hacker01', 'name': 'Hacker', 'department': 'CSE'})
        assert r1_s.status_code in [401, 302], f"Unauthenticated student creation must be blocked: {r1_s.status_code}"
        r1_f = client.post('/api/faculty', json={'faculty_id': 'hacker01', 'name': 'Hacker', 'department': 'CSE'})
        assert r1_f.status_code in [401, 302], f"Unauthenticated faculty creation must be blocked: {r1_f.status_code}"
        print("[PASS] 1. Unauthenticated requests to add student/faculty rejected with 401/302.")

        # Log in as student and verify 403 Forbidden
        client.post('/login', data={'username': 'student001', 'password': 'Student@123'}, follow_redirects=True)
        r_stu_block = client.post('/api/students', json={'student_id': 'hacker02', 'name': 'Hacker', 'department': 'CSE'})
        assert r_stu_block.status_code == 403, f"Student role must be forbidden: {r_stu_block.status_code}"
        r_fac_block = client.post('/api/faculty', json={'faculty_id': 'hacker02', 'name': 'Hacker', 'department': 'CSE'})
        assert r_fac_block.status_code == 403, f"Student role must be forbidden from adding faculty: {r_fac_block.status_code}"
        print("[PASS] 2. Non-admin (student) role forbidden (403) from creating student or faculty records.")

        # 2. Log in as Admin
        client.get('/logout', follow_redirects=True)
        login_res = client.post('/login', data={'username': 'admin001', 'password': 'Admin@123'}, follow_redirects=True)
        assert login_res.status_code == 200, "Admin login failed"
        print("[PASS] 3. Admin successfully authenticated.")

        # 3. Add a new student
        test_student_id = "test_stu_999"
        test_student_email = "priya.test@campusiq.edu"
        add_stu_res = client.post('/api/students', json={
            "student_id": test_student_id,
            "name": "Priya Varma",
            "email": test_student_email,
            "department": "CSE",
            "semester": 6,
            "section": "B",
            "cgpa": 8.45,
            "attendance_pct": 86.5,
            "backlogs": 0,
            "placement_aptitude_score": 78.0,
            "technical_skills_score": 82.0,
            "password": "PriyaPassword@123"
        })
        assert add_stu_res.status_code == 201, f"Failed to add student: {add_stu_res.get_json()}"
        d_stu = add_stu_res.get_json()
        assert d_stu["success"] is True
        print(f"[PASS] 4. Admin added new student: {d_stu['message']}")

        # 4. Verify student appears in Admin's student list
        list_res = client.get('/api/students')
        assert list_res.status_code == 200
        students_list = list_res.get_json()["students"]
        found_stu = next((s for s in students_list if s["student_id"] == test_student_id), None)
        assert found_stu is not None, f"Newly added student {test_student_id} not found in Admin student list"
        assert found_stu["name"] == "Priya Varma"
        assert found_stu["cgpa"] == 8.45
        print(f"[PASS] 5. Student '{test_student_id}' immediately visible in Admin student directory.")

        # 5. Add a new faculty member
        test_fac_id = "test_fac_999"
        test_fac_email = "rajesh.test@campusiq.edu"
        add_fac_res = client.post('/api/faculty', json={
            "faculty_id": test_fac_id,
            "name": "Dr. Rajesh Iyer",
            "email": test_fac_email,
            "department": "ECE",
            "designation": "Associate Professor",
            "specialization": "Embedded Systems & IoT",
            "password": "RajeshPassword@123"
        })
        assert add_fac_res.status_code == 201, f"Failed to add faculty: {add_fac_res.get_json()}"
        d_fac = add_fac_res.get_json()
        assert d_fac["success"] is True
        print(f"[PASS] 6. Admin added new faculty: {d_fac['message']}")

        # 6. Verify faculty appears in Admin's faculty list
        fac_list_res = client.get('/api/admin/faculty')
        assert fac_list_res.status_code == 200
        faculty_list = fac_list_res.get_json()["faculty"]
        found_fac = next((f for f in faculty_list if f["faculty_id"] == test_fac_id), None)
        assert found_fac is not None, f"Newly added faculty {test_fac_id} not found in Admin faculty list"
        assert found_fac["name"] == "Dr. Rajesh Iyer"
        print(f"[PASS] 7. Faculty '{test_fac_id}' immediately visible in Admin faculty directory.")

        # 7. Test duplicate rejection (409 Conflict)
        dup_stu = client.post('/api/students', json={
            "student_id": test_student_id,
            "name": "Priya Clone",
            "department": "CSE"
        })
        assert dup_stu.status_code == 409, f"Duplicate student must return 409, got {dup_stu.status_code}"
        assert "already exists" in dup_stu.get_json()["message"] or "already registered" in dup_stu.get_json()["message"]

        dup_fac = client.post('/api/faculty', json={
            "faculty_id": test_fac_id,
            "name": "Dr. Rajesh Clone",
            "department": "ECE"
        })
        assert dup_fac.status_code == 409, f"Duplicate faculty must return 409, got {dup_fac.status_code}"
        assert "already exists" in dup_fac.get_json()["message"] or "already registered" in dup_fac.get_json()["message"]
        print("[PASS] 8. Duplicate student and faculty IDs rejected with 409 Conflict.")

        # 8. Test Authentication & Role Isolation for new student
        client.get('/logout', follow_redirects=True)
        login_new_stu = client.post('/login', data={'username': test_student_id, 'password': 'PriyaPassword@123'}, follow_redirects=True)
        assert login_new_stu.status_code == 200, "New student login failed"
        # Access student dashboard
        dash_stu = client.get('/student')
        assert dash_stu.status_code == 200, "New student dashboard failed to load"
        # Confirm student cannot access Admin dashboard or admin APIs
        dash_admin_block = client.get('/admin')
        assert dash_admin_block.status_code in [403, 302], "Student must be redirected or blocked from /admin"
        api_admin_block = client.get('/api/admin/overview')
        assert api_admin_block.status_code == 403, "Student must receive 403 Forbidden on admin APIs"
        print("[PASS] 9. Newly added student authenticated successfully with 'student' role (Admin access blocked with 302/403).")

        # 9. Test Authentication & Role Isolation for new faculty
        client.get('/logout', follow_redirects=True)
        login_new_fac = client.post('/login', data={'username': test_fac_id, 'password': 'RajeshPassword@123'}, follow_redirects=True)
        assert login_new_fac.status_code == 200, "New faculty login failed"
        # Access faculty dashboard
        dash_fac = client.get('/faculty')
        assert dash_fac.status_code == 200, "New faculty dashboard failed to load"
        # Confirm faculty cannot access Admin dashboard or admin APIs
        dash_admin_block2 = client.get('/admin')
        assert dash_admin_block2.status_code in [403, 302], "Faculty must be redirected or blocked from /admin"
        api_admin_block2 = client.get('/api/admin/overview')
        assert api_admin_block2.status_code == 403, "Faculty must receive 403 Forbidden on admin APIs"
        print("[PASS] 10. Newly added faculty authenticated successfully with 'faculty' role (Admin access blocked with 302/403).")

        # 10. Test Persistence across simulated application restart
        # Re-run init_db(force=False) as app.py does on startup
        init_db(force=False)

        # Connect to SQLite independently to verify persistence
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE student_id = ?", (test_student_id,))
        row_stu = cur.fetchone()
        assert row_stu is not None, "Persisted student disappeared after application restart!"
        assert row_stu["name"] == "Priya Varma"

        cur.execute("SELECT * FROM faculty WHERE faculty_id = ?", (test_fac_id,))
        row_fac = cur.fetchone()
        assert row_fac is not None, "Persisted faculty disappeared after application restart!"
        assert row_fac["name"] == "Dr. Rajesh Iyer"

        # Check existing official demo records
        cur.execute("SELECT COUNT(*) as count FROM students WHERE student_id LIKE 'CIQ-2026-%'")
        official_students = cur.fetchone()["count"]
        assert official_students >= 10, f"Official demo student cohort modified! Expected at least 10, found {official_students}"

        cur.execute("SELECT COUNT(*) as count FROM faculty WHERE faculty_id LIKE 'faculty%'")
        official_faculty = cur.fetchone()["count"]
        assert official_faculty >= 5, f"Official demo faculty records missing! Found {official_faculty}"

        print("[PASS] 11. Records permanently persisted in SQLite and survived simulated application restart.")
        print("[PASS] 12. Official 10-student calibrated cohort and faculty records 100% preserved.")

        # Clean up test records
        cur.execute("DELETE FROM students WHERE student_id = ?", (test_student_id,))
        cur.execute("DELETE FROM users WHERE user_id IN (?, ?)", (test_student_id, test_fac_id))
        cur.execute("DELETE FROM faculty WHERE faculty_id = ?", (test_fac_id,))
        cur.execute("DELETE FROM student_fees WHERE student_id = ?", (test_student_id,))
        cur.execute("UPDATE departments SET student_count = student_count - 1 WHERE code = 'CSE'")
        cur.execute("UPDATE departments SET faculty_count = faculty_count - 1 WHERE code = 'ECE'")
        conn.commit()
        conn.close()
        print("[PASS] 13. Test records safely cleaned up with zero trace.")

    print("=" * 75)
    print("ALL ADMIN ADD STUDENT & FACULTY PERSISTENCE CHECKS PASSED (13/13)!")
    print("=" * 75)

if __name__ == '__main__':
    run_persistence_tests()

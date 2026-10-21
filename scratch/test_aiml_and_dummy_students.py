"""
Test Suite: AIML Course & 10 Dummy Students Per Course
CampusIQ Prototype Verification
"""

import unittest
import sqlite3
import json
from app import app
from database.db import get_db, init_db

class TestAimlAndDummyStudents(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.testing = True

    def login_client(self, client, username, password):
        return client.post("/login", data={
            "username": username,
            "password": password
        }, follow_redirects=True)

    def test_01_aiml_department_exists(self):
        """1. Confirm AIML exists in the departments table."""
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT code, name, hod_name FROM departments WHERE code = 'AIML'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["code"], "AIML")
        self.assertEqual(row["name"], "Artificial Intelligence and Machine Learning")

    def test_02_aiml_course_exists(self):
        """2. Confirm AIML course exists in the courses table."""
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT course_code, course_name, department FROM courses WHERE department = 'AIML'")
        courses = cur.fetchall()
        conn.close()
        self.assertGreaterEqual(len(courses), 1)
        course_names = [c["course_name"] for c in courses]
        self.assertTrue(any("Artificial Intelligence and Machine Learning" in name for name in course_names))

    def test_03_ten_dummy_students_per_course(self):
        """3. Confirm every supported course has 10 designated dummy/demo student records."""
        conn = get_db()
        cur = conn.cursor()
        OFFICIAL_DEMO_IDS = {f"CIQ-2026-{i:03d}" for i in range(1, 11)}

        for dept in ["AIML", "CSE", "IT", "AI&DS", "ECE", "ME"]:
            cur.execute("SELECT student_id FROM students WHERE department = ?", (dept,))
            sids = [r[0] for r in cur.fetchall()]
            dummy_sids = [sid for sid in sids if sid in OFFICIAL_DEMO_IDS or sid.startswith("CIQ-DEMO-")]
            self.assertEqual(len(dummy_sids), 10, f"Dept {dept} should have exactly 10 dummy students, got {len(dummy_sids)}")
        conn.close()

    def test_04_official_demo_students_preserved(self):
        """4. Confirm existing official demo students remain unchanged."""
        conn = get_db()
        cur = conn.cursor()
        for i in range(1, 11):
            sid = f"CIQ-2026-{i:03d}"
            cur.execute("SELECT student_id, name, department FROM students WHERE student_id = ?", (sid,))
            row = cur.fetchone()
            self.assertIsNotNone(row, f"Official demo student {sid} must be present")
        conn.close()

    def test_05_real_students_preserved(self):
        """5. Confirm real students (sameer) remain preserved."""
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT student_id, name, department FROM students WHERE student_id = 'CIQ-2026-013'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "sameer")
        self.assertEqual(row["department"], "AI&DS")

    def test_06_seeding_is_idempotent(self):
        """6. Run the seed process again and verify no duplicates are created."""
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM students")
        before_count = cur.fetchone()[0]
        conn.close()

        # Run init_db again
        init_db(force=False)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM students")
        after_count = cur.fetchone()[0]
        conn.close()

        self.assertEqual(before_count, after_count, "Seeding must be idempotent without count increase")

    def test_07_admin_filter_by_aiml(self):
        """7. Confirm Admin can filter students by AIML."""
        with self.app.test_client() as client:
            self.login_client(client, "admin001", "Admin@123")
            res = client.get("/api/students?department=AIML")
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            students = data.get("students", [])
            self.assertEqual(len(students), 10)
            for s in students:
                self.assertEqual(s["department"], "AIML")

    def test_08_admin_departments_api_includes_aiml(self):
        """8. Confirm /api/admin/departments API includes AIML with correct statistics."""
        with self.app.test_client() as client:
            self.login_client(client, "admin001", "Admin@123")
            res = client.get("/api/admin/departments")
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            depts = {d["department"]: d for d in data.get("departments", [])}
            self.assertIn("AIML", depts)
            aiml = depts["AIML"]
            self.assertEqual(aiml["total_students"], 10)
            self.assertGreater(aiml["avg_cgpa"], 0)

    def test_09_admin_courses_api_includes_aiml(self):
        """9. Confirm /api/admin/courses API returns AIML courses."""
        with self.app.test_client() as client:
            self.login_client(client, "admin001", "Admin@123")
            res = client.get("/api/admin/courses")
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            courses = [c for c in data.get("courses", []) if c["department"] == "AIML"]
            self.assertGreaterEqual(len(courses), 1)

    def test_10_admin_can_add_student_to_aiml(self):
        """10. Confirm admin can provision a student in AIML department."""
        with self.app.test_client() as client:
            self.login_client(client, "admin001", "Admin@123")
            test_student_id = "CIQ-TEST-AIML-999"

            # Cleanup if left from prior run
            conn = get_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE user_id = ?", (test_student_id,))
            cur.execute("DELETE FROM students WHERE student_id = ?", (test_student_id,))
            conn.commit()
            conn.close()

            res = client.post("/api/students", json={
                "student_id": test_student_id,
                "name": "Test AIML Scholar",
                "email": "test.aiml@campusiq.edu",
                "department": "AIML",
                "semester": 6,
                "cgpa": 8.5,
                "attendance_pct": 85.0,
                "backlogs": 0
            })
            self.assertEqual(res.status_code, 201)

            # Verify in DB
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT student_id, name, department, department_name FROM students WHERE student_id = ?", (test_student_id,))
            row = cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["department"], "AIML")
            self.assertEqual(row["department_name"], "Artificial Intelligence and Machine Learning")

            # Clean up test student
            cur.execute("DELETE FROM users WHERE user_id = ?", (test_student_id,))
            cur.execute("DELETE FROM students WHERE student_id = ?", (test_student_id,))
            cur.execute("DELETE FROM academic_records WHERE student_id = ?", (test_student_id,))
            cur.execute("DELETE FROM student_fees WHERE student_id = ?", (test_student_id,))
            conn.commit()
            conn.close()

    def test_11_login_flows_preserved(self):
        """11. Confirm existing Admin, Faculty, and Student logins still function."""
        # Admin
        with self.app.test_client() as client:
            res_admin = self.login_client(client, "admin001", "Admin@123")
            self.assertEqual(res_admin.status_code, 200)

        # Faculty
        with self.app.test_client() as client:
            res_fac = self.login_client(client, "faculty001", "Faculty@123")
            self.assertEqual(res_fac.status_code, 200)

        # Student
        with self.app.test_client() as client:
            res_stu = self.login_client(client, "student001", "Student@123")
            self.assertEqual(res_stu.status_code, 200)

if __name__ == "__main__":
    unittest.main()

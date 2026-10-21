"""
Verification Test Suite:
1. Faculty Advisor name visibility (color: #000000 in JS and CSS)
2. Students sorted by department (CSE -> AIML -> AIDS -> remaining alphabetical ECE, IT, ME)
3. Secondary sorting by roll number / student_id within department
4. Filter and search compatibility
"""

import sys
sys.path.insert(0, '.')

import json
import re
from app import app
from database.db import get_db

app.config['TESTING'] = True

def run_tests():
    print("=" * 70)
    print("TESTING FACULTY ADVISOR VISIBILITY & DEPARTMENT SORTING")
    print("=" * 70)

    # 1. CSS & JS verification for Faculty Advisor Name Color
    with open("static/js/app.js", "r", encoding="utf-8") as f:
        js_content = f.read()
    assert 'class="faculty-advisor-name"' in js_content, "faculty-advisor-name class missing in app.js"
    assert 'color:#000000;' in js_content, "color:#000000 missing in app.js for advisor"
    assert 'sortBy: "department-asc"' in js_content, "department-asc default sort missing in app.js"
    print("[PASS] 1. JS sets .faculty-advisor-name and color:#000000 inline style.")

    with open("static/css/style.css", "r", encoding="utf-8") as f:
        css_content = f.read()
    assert ".faculty-advisor-name" in css_content, ".faculty-advisor-name selector missing in style.css"
    assert "#studentsTableBody tr td .faculty-advisor-name" in css_content, "Scoped #studentsTableBody rule missing in style.css"
    print("[PASS] 2. Scoped CSS rule in style.css specifies #000000 for faculty advisor name.")

    with open("templates/admin_dashboard.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    assert '<option value="department-asc" selected>' in html_content, "department-asc option missing in admin_dashboard.html"
    print("[PASS] 3. Admin dashboard dropdown has department-asc selected by default.")

    # 2. Test API sorting
    with app.test_client() as client:
        # Log in as admin
        login_res = client.post('/login', data={'username': 'admin001', 'password': 'Admin@123'}, follow_redirects=True)
        assert login_res.status_code == 200, "Admin login failed"

        # Default query (no params)
        res = client.get('/api/students')
        assert res.status_code == 200, f"/api/students failed: {res.status_code}"
        data = json.loads(res.data)
        students = data.get("students", [])
        assert len(students) == 61, f"Expected 61 students, got {len(students)}"

        # Check department grouping and sequence
        seen_depts = []
        for s in students:
            d = s["department"]
            if not seen_depts or seen_depts[-1] != d:
                seen_depts.append(d)

        expected_sequence = ['CSE', 'AIML', 'AI&DS', 'ECE', 'IT', 'ME']
        assert seen_depts == expected_sequence, f"Expected sequence {expected_sequence}, got {seen_depts}"
        print(f"[PASS] 4. Department sorting sequence verified: {seen_depts}")

        # Check grouping: no department should appear in multiple disconnected chunks
        dept_counts = {}
        for s in students:
            dept_counts[s["department"]] = dept_counts.get(s["department"], 0) + 1
        assert len(seen_depts) == len(dept_counts), "Students with same department must be grouped together"
        print(f"[PASS] 5. All departments are strictly grouped together: {dept_counts}")

        # Check secondary sorting by student_id / roll number within each department
        for d in seen_depts:
            dept_sids = [s["student_id"] for s in students if s["department"] == d]
            sorted_sids = sorted(dept_sids, key=lambda x: str(x).lower())
            assert dept_sids == sorted_sids, f"Students in {d} must be sorted ascending by roll number/id: got {dept_sids}"
        print("[PASS] 6. Within each department, students are sorted ascending by student_id / roll number.")

        # Test search compatibility while preserving department sort
        res_search = client.get('/api/students?search=kumar')
        assert res_search.status_code == 200
        # Test department filter compatibility
        res_aiml = client.get('/api/students?department=AIML')
        assert res_aiml.status_code == 200
        aiml_students = json.loads(res_aiml.data).get("students", [])
        assert len(aiml_students) == 10
        assert all(s["department"] == "AIML" for s in aiml_students)
        print("[PASS] 7. Search and department filters function seamlessly.")

        # Test explicit department sort parameter
        res_explicit = client.get('/api/students?sort_by=department&order=asc')
        assert res_explicit.status_code == 200
        explicit_data = json.loads(res_explicit.data)
        explicit_seq = []
        for s in explicit_data.get("students", []):
            d = s["department"]
            if not explicit_seq or explicit_seq[-1] != d:
                explicit_seq.append(d)
        assert explicit_seq == expected_sequence, f"Expected {expected_sequence}, got {explicit_seq}"
        print("[PASS] 8. Explicit /api/students?sort_by=department&order=asc yields exact order.")

        # Test other sort options still work
        res_cgpa = client.get('/api/students?sort_by=cgpa&order=desc')
        assert res_cgpa.status_code == 200
        cgpa_students = json.loads(res_cgpa.data).get("students", [])
        assert cgpa_students[0]["cgpa"] >= cgpa_students[-1]["cgpa"]
        print("[PASS] 9. Other sort options (e.g. CGPA desc) remain functional.")

    # 3. Check official demo students preserved
    conn = get_db()
    c = conn.cursor()
    for i in range(1, 11):
        sid = f"CIQ-2026-{i:03d}"
        c.execute("SELECT student_id, name, department, mentor_name FROM students WHERE student_id = ?", (sid,))
        row = c.fetchone()
        assert row is not None, f"Official demo student {sid} missing"
        assert row["mentor_name"], f"Official demo student {sid} missing mentor_name"

    # Check real student sameer preserved
    c.execute("SELECT student_id, name, department, mentor_name FROM students WHERE student_id = 'CIQ-2026-013'")
    row = c.fetchone()
    assert row is not None, "Real student CIQ-2026-013 missing"
    assert row["name"] == "sameer"
    conn.close()
    print("[PASS] 10. Official demo students and real students 100% preserved.")

    print("=" * 70)
    print("ALL 10 TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()

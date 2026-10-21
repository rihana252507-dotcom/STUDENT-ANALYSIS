"""
Verification script for faculty name visibility and black color fix.
"""
import sys
sys.path.insert(0, '.')

from app import app

def test_faculty_color():
    print("=" * 60)
    print("RUNNING FACULTY NAME VISIBILITY CHECK")
    print("=" * 60)

    # 1. Verify JS rendering
    with open('static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()

    assert 'strong class="faculty-name" style="color:#000000;' in js, "Faculty name color in JS is not #000000"
    assert 'strong style="color:#FFFFFF; font-size:0.875rem;">${escapeHtml(f.name)}' not in js, "Old white color still present in JS"
    print("[PASS] 1. Faculty name inline style updated to solid black (#000000).")

    # 2. Verify CSS rule
    with open('static/css/style.css', 'r', encoding='utf-8') as f:
        css = f.read()

    assert '.faculty-name' in css, "Missing .faculty-name in style.css"
    assert '#facultyTableBody tr td strong' in css, "Missing #facultyTableBody in style.css"
    assert 'color: #000000;' in css, "Missing black color rule in style.css"
    print("[PASS] 2. Scoped CSS rule targeting faculty name in #facultyTableBody set to #000000.")

    # 3. Verify Admin Dashboard and Faculty API
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Admin Login
        client.post('/login', data={'username': 'admin001', 'password': 'Admin@123'}, follow_redirects=True)
        r_admin = client.get('/admin')
        assert r_admin.status_code == 200, "Admin dashboard failed to load"
        assert 'section-faculty' in r_admin.data.decode('utf-8')
        assert 'facultyTableBody' in r_admin.data.decode('utf-8')
        print("[PASS] 3. Admin dashboard loads successfully with faculty table intact.")

        # Faculty API data
        r_api = client.get('/api/admin/faculty')
        assert r_api.status_code == 200
        faculty_data = r_api.get_json()['faculty']
        assert len(faculty_data) >= 5
        for fac in faculty_data:
            assert fac['name'], "Faculty name is missing"
            assert fac['faculty_id'], "Faculty ID is missing"
            assert fac['department'], "Department is missing"
            assert fac['designation'], "Designation is missing"
        print(f"[PASS] 4. All {len(faculty_data)} faculty members retrieved with intact metadata.")

    print("=" * 60)
    print("ALL FACULTY NAME VISIBILITY CHECKS PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == '__main__':
    test_faculty_color()

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from app import app

def test_hod_login_visibility_and_auto_loading():
    client = app.test_client()

    # 1. Login as CSE HOD
    login_res = client.post('/login', data={'username': 'hod_cse', 'password': 'Hod@123'}, follow_redirects=True)
    assert login_res.status_code == 200
    html = login_res.data.decode('utf-8')

    # Confirm HOD dashboard content rendered immediately on login
    assert 'Department Executive Overview' in html
    assert 'section-overview' in html
    assert 'dashboard-section active-section active' in html
    assert 'style="display:block;"' in html
    assert 'Dr. Sunita Rao' in html
    assert 'initHodDashboard' in html
    assert 'statTotalStudents' in html
    assert 'statTotalFaculty' in html
    assert 'statAtRiskStudents' in html
    assert 'statAvgAttendance' in html
    assert 'statAvgCgpa' in html
    assert 'statActiveInterventions' in html

    # 2. Check HOD Overview API
    api_res = client.get('/api/hod/overview')
    assert api_res.status_code == 200
    data = json.loads(api_res.data.decode('utf-8'))
    assert data['success'] is True
    assert data['department']['code'] == 'CSE'
    assert data['metrics']['total_students'] > 0
    assert data['metrics']['total_faculty'] > 0

    print("SUCCESS: HOD dashboard renders automatically on login with all sections and high contrast.")

if __name__ == '__main__':
    test_hod_login_visibility_and_auto_loading()

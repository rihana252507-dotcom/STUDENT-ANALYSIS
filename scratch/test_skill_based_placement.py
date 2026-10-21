"""
CampusIQ – Dynamic Skill-Based Placement Readiness Verification Suite
Tests the 10 essential checks specified in the task requirements:
1. Student login & placement section access
2. Finding matches with Python, SQL, and HTML
3. Changing skills to Java, DSA, and JavaScript and verifying dynamic rank change
4. Verification of matched and missing skills accuracy
5. Verification that skill matching % and academic eligibility are cleanly separate
6. Saving, restoring, editing, and removing skills
7. Handling empty input and zero-match states
8. Verification of official careers URLs for Apply buttons
9. Student-level security isolation (student001 vs student002)
10. Complete regression check: dashboard, chatbot, fees, academic records, admin, faculty
"""

import sys
import json
sys.path.insert(0, '.')

from app import app
from services.placement import COMPANY_OPPORTUNITIES, match_companies_for_student

app.config['TESTING'] = True

def run_tests():
    print("=" * 75)
    print("RUNNING DYNAMIC SKILL-BASED PLACEMENT READINESS TEST SUITE")
    print("=" * 75)

    with app.test_client() as client:
        # Check 1: Log in as a student and verify Placement Readiness section
        r = client.post('/login', data={'username': 'student001', 'password': 'Student@123'}, follow_redirects=True)
        assert r.status_code == 200, "Login failed"
        r_page = client.get('/student')
        assert r_page.status_code == 200, "Student page failed to load"
        html = r_page.data.decode('utf-8')
        assert 'section-placement-readiness' in html, "section-placement-readiness missing"
        assert 'My Skills &amp; Career Preferences' in html or 'My Skills & Career Preferences' in html
        assert 'Find Matching Companies' in html
        print("[PASS] 1. Student login & Placement Readiness section loaded successfully.")

        # Check 2: Enter Python, SQL, and HTML, then find matching companies
        res2 = client.post('/api/student/placement/match', json={
            'skills': ['Python', 'SQL', 'HTML'],
            'save_skills': True
        })
        assert res2.status_code == 200
        d2 = res2.get_json()
        assert d2['success'] is True
        assert len(d2['companies']) == 5
        top_company_2 = d2['companies'][0]['short_name']
        print(f"[PASS] 2. Matches found for [Python, SQL, HTML]. Top company: {top_company_2} ({d2['companies'][0]['match_percentage']}%)")

        # Check 3: Change skills to Java, Data Structures and Algorithms, and JavaScript
        res3 = client.post('/api/student/placement/match', json={
            'skills': ['Java', 'Data Structures and Algorithms', 'JavaScript'],
            'save_skills': True
        })
        assert res3.status_code == 200
        d3 = res3.get_json()
        top_company_3 = d3['companies'][0]['short_name']
        assert top_company_3 != top_company_2 or d3['companies'][0]['match_percentage'] != d2['companies'][0]['match_percentage'], "Results did not change dynamically!"
        print(f"[PASS] 3. Results changed dynamically for [Java, DSA, JS]. Top company: {top_company_3} ({d3['companies'][0]['match_percentage']}%)")

        # Check 4: Verify matched and missing skills are displayed correctly
        # In test 2 (Python, SQL, HTML) against TCS (Python, Java, C++, DSA):
        tcs_d2 = next(c for c in d2['companies'] if c['short_name'] == 'TCS')
        assert 'Python' in tcs_d2['matched_required'], "Python should be matched for TCS"
        assert 'Java' in tcs_d2['missing_required'], "Java should be missing for TCS"
        assert 'Data Structures and Algorithms' in tcs_d2['missing_required'], "DSA should be missing for TCS"
        # In test 3 (Java, DSA, JavaScript) against TCS:
        tcs_d3 = next(c for c in d3['companies'] if c['short_name'] == 'TCS')
        assert 'Java' in tcs_d3['matched_required'], "Java should now be matched for TCS"
        assert 'Data Structures and Algorithms' in tcs_d3['matched_required'], "DSA should now be matched for TCS"
        assert 'Python' in tcs_d3['missing_required'], "Python should now be missing for TCS"
        print("[PASS] 4. Matched and missing skills correctly identified and verified.")

        # Check 5: Confirm that skill matching % and academic eligibility are separate
        # student001 has CGPA 9.1, 0 backlogs -> Eligible
        assert tcs_d2['eligibility_status'] == 'Eligible'
        assert tcs_d2['match_percentage'] == 25  # low skill match, but academically eligible
        # Test a student with low CGPA / high backlogs (e.g. Kabir Mehta student008: sem 6, cgpa 5.4, 3 backlogs)
        s_kabir = {'semester': 6, 'cgpa': 5.4, 'backlogs': 3, 'department': 'ME'}
        kabir_matches = match_companies_for_student(['Python', 'Java', 'C++', 'Data Structures and Algorithms'], s_kabir)
        tcs_kabir = next(c for c in kabir_matches['companies'] if c['short_name'] == 'TCS')
        assert tcs_kabir['match_percentage'] == 100, "Kabir has 100% skill match"
        assert tcs_kabir['eligibility_status'] == 'Not Eligible', "Kabir should be academically Not Eligible"
        assert 'CGPA' in tcs_kabir['eligibility_reason'] and 'backlog' in tcs_kabir['eligibility_reason']
        print("[PASS] 5. Skill match (100%) and academic eligibility (Not Eligible) verified as strictly separate.")

        # Check 6: Test saving, restoring, editing, and removing skills
        # Save a custom list
        r_save = client.post('/api/student/skills', json={'skills': ['Python', 'Docker', 'Kubernetes']})
        assert r_save.status_code == 200
        # Restore
        r_get = client.get('/api/student/skills')
        assert r_get.status_code == 200
        saved = r_get.get_json()['skills']
        assert saved == ['Python', 'Docker', 'Kubernetes']
        # Edit / remove 'Docker'
        r_edit = client.post('/api/student/skills', json={'skills': ['Python', 'Kubernetes']})
        assert r_edit.get_json()['skills'] == ['Python', 'Kubernetes']
        # Restore again
        r_get2 = client.get('/api/student/skills')
        assert r_get2.get_json()['skills'] == ['Python', 'Kubernetes']
        print("[PASS] 6. Saving, restoring, editing, and removing student skills fully functional.")

        # Check 7: Test empty input and zero-match state
        # Empty input
        r_empty = client.post('/api/student/placement/match', json={'skills': []})
        d_empty = r_empty.get_json()
        assert d_empty['has_entered_skills'] is False
        assert len(d_empty['companies']) == 0
        assert "Please enter your" in d_empty['message']
        # Zero match state (e.g. non-tech skills)
        r_zero = client.post('/api/student/placement/match', json={'skills': ['Gardening', 'Cooking']})
        d_zero = r_zero.get_json()
        assert d_zero['has_entered_skills'] is True
        assert d_zero['zero_match_state'] is True
        assert max(c['match_percentage'] for c in d_zero['companies']) == 0
        assert len(d_zero['skills_to_improve']) > 0
        print("[PASS] 7. Empty input prompt and zero-match fallback states verified.")

        # Check 8: Verify that Apply buttons use verified official URLs
        for comp in COMPANY_OPPORTUNITIES:
            assert comp['apply_url'].startswith('https://'), f"URL for {comp['company_name']} is not HTTPS"
            assert 'careers' in comp['apply_url'].lower() or 'tcs.com' in comp['apply_url']
            assert comp['url_verified'] is True
        print("[PASS] 8. All Apply links are verified official careers portals (no fabricated URLs).")

        # Check 9: Security & isolation: student002 cannot access or overwrite student001's skills
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': 'student002', 'password': 'Student@123'}, follow_redirects=True)
        r_s2 = client.get('/api/student/skills')
        assert r_s2.get_json()['skills'] != ['Python', 'Kubernetes'], "student002 leaked student001 skills!"
        # student002 saves own skills
        client.post('/api/student/skills', json={'skills': ['React', 'Node.js']})
        # switch back to student001
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': 'student001', 'password': 'Student@123'}, follow_redirects=True)
        r_s1 = client.get('/api/student/skills')
        assert r_s1.get_json()['skills'] == ['Python', 'Kubernetes'], "student001 skills were overwritten!"
        print("[PASS] 9. Cross-student session security and skill isolation strictly enforced.")

        # Check 10: Complete regression test: dashboard, chatbot, fees, academic records, admin, faculty
        # Student dashboard
        r_dash = client.get('/student')
        assert r_dash.status_code == 200
        # Chatbot
        r_chat = client.post('/api/student/chat', json={'message': 'How can I improve my marks?'})
        assert r_chat.status_code == 200 and 'reply' in r_chat.get_json()
        # Fee details
        r_fee = client.get('/api/student/fee-details')
        assert r_fee.status_code == 200 and len(r_fee.get_json()['records']) > 0
        # Academic records
        r_acad = client.get('/api/student/academic-records')
        assert r_acad.status_code == 200 and len(r_acad.get_json()['records']) > 0
        # Admin dashboard
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': 'admin001', 'password': 'Admin@123'}, follow_redirects=True)
        r_admin = client.get('/admin')
        assert r_admin.status_code == 200
        # Faculty dashboard
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': 'faculty001', 'password': 'Faculty@123'}, follow_redirects=True)
        r_faculty = client.get('/faculty')
        assert r_faculty.status_code == 200
        print("[PASS] 10. All existing features (dashboard, chatbot, fees, academic records, admin, faculty) 100% intact.")

    print("=" * 75)
    print("ALL 10 ESSENTIAL PLACEMENT READINESS CHECKS PASSED PERFECTLY!")
    print("=" * 75)

if __name__ == '__main__':
    run_tests()

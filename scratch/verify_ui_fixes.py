"""Verify all UI changes are correct."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS"

checks = {
    'templates/admin_dashboard.html': [
        ('recorded in the system.', True, 'SQLite subtitle replaced'),
        ('Live Activity Feed', True, 'SQLite badge replaced'),
        ('Live SQLite Feed', False, 'Old SQLite badge gone'),
        ('color:#5B6B82;">6 Students', True, 'Placement KPI1 light color'),
        ('color:#5B6B82;">Quantitative', True, 'Placement KPI2 light color'),
        ('color:#5B6B82;">Algorithms', True, 'Placement KPI3 light color'),
        ('background:rgba(18,59,102,0.6)', False, 'Reports dark bg gone'),
        ('background:#FFFFFF', True, 'Reports light bg present'),
        ('background:rgba(30,15,60,0.6)', False, 'Settings dark bg gone'),
        ('background:#F4F7FB', True, 'Settings light bg present'),
        ('color:#C4B5FD; font-weight:700;">1. ACADEMIC', False, 'Settings label dark color gone'),
        ('color:#5B6B82; font-weight:700;">1. ACADEMIC', True, 'Settings label light color present'),
    ],
    'static/js/app.js': [
        ('section-risk-monitoring', True, 'Risk monitoring refresh hook present'),
        ('renderAdminRiskList(STATE.atRiskStudents)', True, 'Risk list re-render call present'),
        ('saved to SQLite!', False, 'Old SQLite alert gone'),
        ('saved successfully!', True, 'New alert present'),
    ],
    'templates/faculty_dashboard.html': [
        ('Save to SQLite', False, 'SQLite button gone'),
        ('Save Intervention', True, 'Save Intervention button present'),
        ('Save Progress to SQLite', False, 'Old Progress SQLite button gone'),
        ('Save Progress', True, 'Save Progress button present'),
    ],
}

all_ok = True
for filepath, tests in checks.items():
    with open(BASE + '\\' + filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    for needle, should_exist, label in tests:
        found = needle in content
        status = 'OK' if found == should_exist else 'FAIL'
        if status == 'FAIL':
            all_ok = False
        print(f'  [{status}] {label}')

print()
print('ALL CHECKS PASSED' if all_ok else 'SOME CHECKS FAILED')

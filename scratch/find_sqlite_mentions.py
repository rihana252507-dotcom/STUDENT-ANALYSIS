import re

# 1. Search for SQLite in templates/admin_dashboard.html and static/js/app.js
for path in ['templates/admin_dashboard.html', 'static/js/app.js', 'templates/faculty_dashboard.html', 'templates/student_dashboard.html', 'templates/hod_dashboard.html']:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        if 'sqlite' in line.lower():
            print(f"{path}:{idx}: {line.strip()[:120]}")

import os

files_to_check = [
    'templates/admin_dashboard.html',
    'templates/faculty_dashboard.html',
    'templates/student_dashboard.html',
    'templates/hod_dashboard.html',
    'static/js/app.js'
]

for fpath in files_to_check:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f, 1):
                if any(w in line.lower() for w in ['export', 'download', 'csv', 'xlsx']):
                    print(f"{fpath}:{idx}: {line.strip()[:110]}")

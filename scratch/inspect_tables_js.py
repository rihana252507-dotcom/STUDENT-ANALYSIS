with open('static/js/app.js', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if any(k in line for k in ['renderStudentTable', 'facultyStudent', 'renderFaculty', 'modalBacklogs', 'inspectStudent']):
        print(f"{i}: {line.strip()[:100]}")

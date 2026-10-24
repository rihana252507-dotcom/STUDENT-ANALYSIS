with open('templates/student_dashboard.html', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if '#D4E9FF' in l.upper() or '#C4B5FD' in l.upper():
        print(f"{i}: {l.strip()[:100]}")

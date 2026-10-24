with open('templates/student_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if any(k in l.lower() for k in ['export', 'download', 'csv', 'xlsx', 'report', 'print']):
        print(f'{i}: {l.strip()[:100]}')

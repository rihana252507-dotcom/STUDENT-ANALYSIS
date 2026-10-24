for template in ['templates/admin_dashboard.html', 'templates/faculty_dashboard.html']:
    with open(template, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        if 'intervention' in line.lower() and ('export' in line.lower() or 'download' in line.lower() or 'csv' in line.lower()):
            print(f"{template}:{idx}: {line.strip()}")

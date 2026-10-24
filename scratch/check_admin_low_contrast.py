with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if any(k in line.lower() for k in ['sqlite', '#c4b5fd', '#d4e9ff']):
        print(f"{idx}: {line.strip()[:120]}")

with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '<form' in l or 'modal' in l.lower() or 'button' in l.lower() and ('add' in l.lower() or 'create' in l.lower() or 'register' in l.lower()):
        print(f"{i+1}: {l.strip()[:100]}")

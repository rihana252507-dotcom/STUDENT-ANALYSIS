with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if 'csv' in l.lower() or 'export' in l.lower() or 'xlsx' in l.lower():
        if '@app.route' in l or 'def ' in l:
            print(f'{i}: {l.strip()}')

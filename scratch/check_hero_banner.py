with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'hero-glass-banner' in l:
        for j in range(i, min(i+35, len(lines))):
            print(f'{j+1}: {lines[j]}', end='')
        break

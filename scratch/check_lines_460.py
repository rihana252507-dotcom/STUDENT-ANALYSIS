with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(455, min(485, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')

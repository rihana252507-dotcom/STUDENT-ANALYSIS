with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(394, 430):
    print(f'{i+1}: {lines[i]}', end='')

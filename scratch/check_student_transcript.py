with open('templates/student_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(585, min(630, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if any(k in l for k in ['def admin_dashboard', 'def faculty_dashboard', 'def student_dashboard']):
        for j in range(max(0, i-4), min(len(lines), i+6)):
            print(f'{j+1}: {lines[j]}', end='')
        print('---')

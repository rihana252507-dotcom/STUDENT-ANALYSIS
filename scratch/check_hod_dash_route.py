with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '/hod/dashboard' in l or 'def hod_dashboard' in l:
        for j in range(max(0, i-5), min(len(lines), i+15)):
            print(f'{j+1}: {lines[j]}', end='')
        break

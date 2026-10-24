with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'def add_faculty' in l:
        for j in range(i, min(len(lines), i+65)):
            print(f"{j+1}: {lines[j]}", end='')
        break

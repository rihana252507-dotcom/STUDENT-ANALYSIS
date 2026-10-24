with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2680, min(2760, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')

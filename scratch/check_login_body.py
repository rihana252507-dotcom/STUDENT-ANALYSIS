with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '@app.route("/login"' in l:
        for j in range(i, min(i+50, len(lines))):
            print(f'{j+1}: {lines[j]}', end='')
        break

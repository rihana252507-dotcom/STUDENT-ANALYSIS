with open('static/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2470, min(2520, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')

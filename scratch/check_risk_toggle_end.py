with open('static/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1440, 1475):
    print(f"{i+1}: {lines[i].encode('ascii', errors='replace').decode('ascii')}", end='')

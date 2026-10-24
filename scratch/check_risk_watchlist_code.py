with open('static/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(945, 1060):
    print(f"{i+1}: {lines[i]}", end='')

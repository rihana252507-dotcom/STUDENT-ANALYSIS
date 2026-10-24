with open('static/css/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(300, 320):
    print(f"{i+1}: {lines[i]}", end='')

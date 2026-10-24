with open('templates/login.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(120, len(lines)):
    print(f"{i+1}: {repr(lines[i])}")

with open('templates/login.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(115, 145):
    print(f"{i+1}: {repr(lines[i])}")

with open('templates/login.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(70, 140):
    print(f"{i+1}: {lines[i]}", end='')

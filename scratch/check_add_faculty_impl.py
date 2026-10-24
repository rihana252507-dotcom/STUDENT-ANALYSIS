with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(964, 995):
    print(f"{i+1}: {lines[i]}", end='')

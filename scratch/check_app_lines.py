with open('app.py', encoding='utf-8') as f:
    lines = f.readlines()

for j in range(570, 625):
    print(f"{j+1}: {lines[j].rstrip()}")

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- lines 915-945 ---")
for i in range(914, 945):
    print(f"{i+1}: {lines[i]}", end='')

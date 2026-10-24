with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- index() and login() (lines 50-95) ---")
for i in range(50, 95):
    print(f"{i+1}: {lines[i]}", end='')

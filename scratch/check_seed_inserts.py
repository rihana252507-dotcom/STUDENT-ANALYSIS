with open('database/db.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'INSERT INTO users' in line or 'INSERT OR IGNORE INTO users' in line:
        for j in range(max(0, i-2), min(len(lines), i+35)):
            print(f"{j+1}: {lines[j]}", end='')
        print("\n" + "="*50 + "\n")

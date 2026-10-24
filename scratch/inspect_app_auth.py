with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines[:300]):
    if any(k in line for k in ['login', 'session', 'role', 'def admin', 'def faculty', 'def student']):
        print(f"{i+1}: {line.strip()[:100]}")

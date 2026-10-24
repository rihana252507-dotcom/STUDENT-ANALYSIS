with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '@app.route("/api/' in l:
        print(f"{i+1}: {l.strip()}")

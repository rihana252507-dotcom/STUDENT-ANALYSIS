with open('database/db.py', 'r', encoding='utf-8') as f:
    text = f.read()

for line in text.splitlines():
    if 'CREATE TABLE' in line:
        print(line.strip())

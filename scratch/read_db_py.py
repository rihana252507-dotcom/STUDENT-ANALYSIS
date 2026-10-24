with open('database/db.py', 'r', encoding='utf-8') as f:
    text = f.read()

print("Length of db.py:", len(text))
print(text[:1500])

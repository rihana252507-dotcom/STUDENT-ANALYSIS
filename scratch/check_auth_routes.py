with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Inspect secret key
for line in text.splitlines()[:50]:
    if 'secret_key' in line.lower():
        print(line)

# Inspect index and login routes
idx = text.find('@app.route("/")')
if idx != -1:
    print(text[idx:idx+1200])

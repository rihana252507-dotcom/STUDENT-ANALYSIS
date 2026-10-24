with open('services/analytics.py', 'r', encoding='utf-8') as f:
    text = f.read()

print("Length of services/analytics.py:", len(text))
for line in text.splitlines()[:40]:
    print(line)

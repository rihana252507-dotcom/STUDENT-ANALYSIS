with open('services/auth.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('def role_required')
print(text[idx:])

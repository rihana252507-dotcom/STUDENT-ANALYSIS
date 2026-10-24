with open('services/auth.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('if not user:')
idx2 = text.find('def login_user')
print(text[idx:idx2+500])

with open('services/auth.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('def authenticate_user')
if idx != -1:
    print(text[idx:idx+1000])

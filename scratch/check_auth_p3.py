with open('services/auth.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('def login_user')
idx2 = text.find('def get_current_user')
print(text[idx:idx2+400])

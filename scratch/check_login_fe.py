with open('templates/login.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('fetch(')
if idx != -1:
    print('Found fetch in login.html:')
    print(text[idx-100:idx+400])
else:
    print('No fetch in login.html')

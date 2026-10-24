with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('Faculty Management')
if idx != -1:
    print(text[idx:idx+800])
else:
    idx = text.find('Faculty')
    print(text[idx:idx+400])

with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="section-settings"')
if idx != -1:
    print(text[idx:idx+1500])

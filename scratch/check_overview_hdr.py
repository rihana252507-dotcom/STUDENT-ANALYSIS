with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="section-overview"')
if idx != -1:
    print(text[idx:idx+800])

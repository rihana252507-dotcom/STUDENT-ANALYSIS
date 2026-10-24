with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="section-settings"')
idx2 = text.find('</section>', idx)
print(text[idx:idx2+20])

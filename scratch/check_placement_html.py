with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="section-placement"')
idx2 = text.find('id="section-reports"', idx)
print(text[idx:idx2])

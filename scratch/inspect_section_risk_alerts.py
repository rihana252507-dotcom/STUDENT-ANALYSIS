with open('templates/faculty_dashboard.html', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="section-risk-alerts"')
print(text[idx:idx+2000])

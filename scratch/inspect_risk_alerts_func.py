with open('static/js/app.js', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function renderRiskAlertsTable(students)')
print(text[idx:idx+2500])

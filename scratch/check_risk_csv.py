with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

if 'exportRiskCSV' in text:
    print('Found exportRiskCSV in static/js/app.js')
else:
    print('exportRiskCSV NOT found in static/js/app.js')

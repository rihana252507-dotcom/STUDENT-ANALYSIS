with open('static/js/app.js', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('const tbody = document.getElementById("academicPerfTableBody");')
print("=== academicPerfTableBody function ===")
print(text[idx1-100:idx1+1500])

idx2 = text.find('const tbody = document.getElementById("riskAlertsTableBody");')
print("\n=== riskAlertsTableBody function ===")
print(text[idx2-100:idx2+1500])

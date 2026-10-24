with open('static/js/app.js', encoding='utf-8') as f:
    text = f.read()

import re
for m in re.finditer(r'([^\n]*academicPerfTableBody[^\n]*)', text):
    print("Line:", m.group(1))

# Also search for riskAlertsTableBody
for m in re.finditer(r'([^\n]*riskAlertsTableBody[^\n]*)', text):
    print("Risk alerts line:", m.group(1))

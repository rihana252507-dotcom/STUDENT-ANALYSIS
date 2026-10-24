with open('static/js/app.js', encoding='utf-8') as f:
    text = f.read()

import re
print("Matches in app.js:")
for m in re.finditer(r'academicPerfTableBody|riskAlertsTableBody|academicPerf|riskAlert', text):
    start = max(0, m.start() - 40)
    end = min(len(text), m.end() + 80)
    print(repr(text[start:end]))

print("\nMatches in templates/faculty_dashboard.html:")
with open('templates/faculty_dashboard.html', encoding='utf-8') as f:
    ftext = f.read()
for m in re.finditer(r'academicPerfTableBody|riskAlertsTableBody', ftext):
    start = max(0, m.start() - 100)
    end = min(len(ftext), m.end() + 200)
    print(repr(ftext[start:end]))

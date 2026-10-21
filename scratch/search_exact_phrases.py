with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'(?i)(?:low risk|attendance students)', text)
print('matches in admin_dashboard.html:', matches)

with open('static/js/app.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

matches_js = re.findall(r'(?i)(?:low risk|attendance students)', js_text)
print('matches in app.js:', matches_js)

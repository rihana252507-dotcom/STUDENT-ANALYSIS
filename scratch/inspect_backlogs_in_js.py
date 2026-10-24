with open('static/js/app.js', encoding='utf-8') as f:
    text = f.read()

import re
print("Backlog references in app.js:")
for m in re.finditer(r'([^\n]{0,40}backlog[^\n]{0,60})', text, re.IGNORECASE):
    print(" ", m.group(1).strip())

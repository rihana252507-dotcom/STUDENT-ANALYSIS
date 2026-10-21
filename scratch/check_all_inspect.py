with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'inspectStudent', text)]
for idx in matches:
    print("--- Match at index", idx, "---")
    print(text[max(0, idx-50):min(len(text), idx+300)])

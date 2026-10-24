with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'placement', text, re.IGNORECASE)]
print(f"Total 'placement' occurrences in app.js: {len(matches)}")
for idx in matches:
    print(text[max(0, idx-50):min(len(text), idx+100)])
    print("-" * 30)

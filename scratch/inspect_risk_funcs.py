with open('static/js/app.js', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'function\s+render[a-zA-Z0-9_]*Risk[a-zA-Z0-9_]*\([^)]*\)', text)
print("Risk render functions in app.js:", matches)
for m in matches:
    idx = text.find(m)
    print(f"\n--- {m} ---")
    print(text[idx:idx+600])

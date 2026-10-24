with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'[a-zA-Z0-9_]*setting[a-zA-Z0-9_]*', text, re.IGNORECASE)
print("Settings matches in app.js:", set(matches))

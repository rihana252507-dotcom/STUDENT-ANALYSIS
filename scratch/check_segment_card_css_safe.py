with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'\.segment-card\b', text)
if m:
    safe = text[m.start():m.start()+800].encode('ascii', 'replace').decode('ascii')
    print(safe)

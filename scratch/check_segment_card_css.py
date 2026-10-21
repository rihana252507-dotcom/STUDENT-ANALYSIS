with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'\.segment-card\b', text)
if m:
    print(text[m.start():m.start()+800])

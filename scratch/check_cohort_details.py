with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'function updateCohortSegments', text)
if m:
    print(text[m.start():m.start()+800])

with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'function updateCohortSegments', text)
if m:
    idx = m.start()
    print(text[idx:idx+1200].encode('ascii', 'replace').decode('ascii'))

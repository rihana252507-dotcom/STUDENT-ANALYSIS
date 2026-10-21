with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'inspectStudent', text)
if m:
    print(text[m.start()-100:m.start()+2000])

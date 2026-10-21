with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'studentDetailModal', text)
if m:
    print(text[m.start()-50:m.start()+800])

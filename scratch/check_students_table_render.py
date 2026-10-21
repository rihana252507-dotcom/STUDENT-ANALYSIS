with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'studentsTableBody', text)
if m:
    # search backwards from m
    idx = text.rfind('function', 0, m.start())
    print(text[idx:idx+2500])

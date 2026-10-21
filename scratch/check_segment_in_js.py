with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'class="segment-card', text)]
print('segment-card in app.js:', matches)

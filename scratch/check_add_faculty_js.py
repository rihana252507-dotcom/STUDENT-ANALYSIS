with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'addFacultyForm', text)]
for idx in matches:
    print(text[idx-50:idx+450])

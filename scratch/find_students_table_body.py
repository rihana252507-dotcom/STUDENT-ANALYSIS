with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'studentsTableBody', text)]
print('studentsTableBody matches:', matches)
for idx in matches:
    print(text[max(0, idx-200):min(len(text), idx+500)])

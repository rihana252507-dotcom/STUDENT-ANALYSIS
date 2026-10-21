with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'openStudentModal|inspectStudent', text)]
print("Total matches:", len(matches))

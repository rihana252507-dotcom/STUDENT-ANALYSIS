with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'function filterStudents|filterRisk|filterDepartment|searchStudents', text)
if m:
    print(text[m.start()-50:m.start()+1500])
else:
    print("Not found, searching input listeners...")
    m2 = re.search(r'filter|search', text)
    print("Found keyword at", m2.start())

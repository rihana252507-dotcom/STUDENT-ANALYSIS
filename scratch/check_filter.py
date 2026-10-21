with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'function filterStudents', text)
if m:
    print(text[m.start():m.start()+1000])

m2 = re.search(r'renderStudentsTable', text)
if m2:
    print(text[m2.start():m2.start()+1000])

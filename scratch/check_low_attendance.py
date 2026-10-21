with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'Low Attendance', text)
if m:
    print("Found Low Attendance at index", m.start())
    print(text[m.start()-200:m.start()+800])

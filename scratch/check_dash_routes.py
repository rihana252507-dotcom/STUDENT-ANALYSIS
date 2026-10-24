with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
routes = re.findall(r'@app\.route\([^\)]+\)\n(?:@login_required\n)?(?:@role_required\([^\)]+\)\n)?def \w+\(', text)
for r in routes:
    if any(k in r for k in ['dashboard', 'admin', 'faculty', 'student', 'hod']):
        print(r)
        print('---')

with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
keywords = ['create', 'faculty', 'user', 'account', 'modal', 'add']
for k in keywords:
    matches = re.findall(rf'.{{0,40}}{k}.{{0,40}}', text, re.IGNORECASE)
    print(f"Keyword '{k}': {len(matches)} occurrences")

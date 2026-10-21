with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'class="segment-card', text)]
for idx in matches:
    print(text[idx:idx+700])
    print("="*50)

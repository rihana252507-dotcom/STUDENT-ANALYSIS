with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'class="segment-card', text)
if m:
    print(text[m.start()-50:m.start()+2500])

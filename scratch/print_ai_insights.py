with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'section-ai-insights', text)
if m:
    start = m.start()
    print(text[start:start+4000])

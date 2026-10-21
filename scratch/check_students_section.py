with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'<section id="section-students".*?</section>', text, re.DOTALL)
if m:
    print(m.group(0)[:3000])

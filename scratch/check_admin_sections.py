with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.findall(r'<section id="([^"]+)"[^>]*>.*?<h2[^>]*>(.*?)</h2>', text, re.DOTALL)
for s_id, s_title in sections:
    print(f"Section {s_id} -> {s_title.strip()[:60]}")

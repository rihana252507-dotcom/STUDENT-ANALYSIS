with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.findall(r'<section\s+id="([^"]+)"[^>]*>', text)
print("Sections in admin_dashboard.html:", sections)

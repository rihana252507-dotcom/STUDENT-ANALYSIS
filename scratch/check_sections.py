import re

with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

sections = re.findall(r'id=["\'](section-[^"\']+)["\']', text)
print('Existing sections:', sections)

with open('templates/faculty_dashboard.html', encoding='utf-8') as f:
    text = f.read()

import re
print("Backlog mentions in faculty_dashboard.html:")
for m in re.finditer(r'.{0,50}backlog.{0,50}', text, re.IGNORECASE):
    print(" ", m.group(0).strip())

print("\nScripts in faculty_dashboard.html:")
for m in re.finditer(r'<script[^>]*>.*?</script>', text, re.DOTALL):
    print(m.group(0)[:200])

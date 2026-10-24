with open('templates/student_dashboard.html', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'<section[^>]*id=["\']([^"\']*)["\'][^>]*>', text)
print("Sections in student_dashboard.html:")
for m in matches:
    print(" ", m.group(1))

# Search for attendance section
idx = text.find('id="section-attendance"')
if idx != -1:
    print("\n=== section-attendance in student_dashboard.html ===")
    print(text[idx:idx+3500])
else:
    print("section-attendance not found by that id")

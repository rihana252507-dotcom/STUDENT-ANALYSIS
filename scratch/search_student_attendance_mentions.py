with open('templates/student_dashboard.html', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'([^\n]{0,50}attendance[^\n]{0,50})', text, re.IGNORECASE)
print("All attendance mentions in student_dashboard.html:")
for m in matches:
    print(" ", m.group(1).strip())

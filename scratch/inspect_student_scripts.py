with open('templates/student_dashboard.html', encoding='utf-8') as f:
    text = f.read()

import re
print("Scripts in student_dashboard.html:")
for m in re.finditer(r'<script[^>]*>.*?</script>', text, re.DOTALL):
    print(m.group(0)[:150])

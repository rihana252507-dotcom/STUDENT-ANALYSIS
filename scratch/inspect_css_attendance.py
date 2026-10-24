with open('static/css/style.css', encoding='utf-8') as f:
    css = f.read()

import re
print("Matches for attendance in style.css:")
for m in re.finditer(r'([^\n\{]*attendance[^\n\{]*\{[^\}]*\})', css, re.IGNORECASE):
    print(" ", m.group(1)[:200])

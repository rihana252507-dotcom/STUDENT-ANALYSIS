with open('templates/login.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'<form.*?</form>', text, re.DOTALL)
if m:
    print(m.group(0))

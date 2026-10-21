with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'window\.inspectStudent\s*=\s*async\s*function', text)
if m:
    start = m.start()
    lines = text[start:].splitlines()[:80]
    for i, line in enumerate(lines):
        # escape non-ascii
        safe_line = line.encode('ascii', 'replace').decode('ascii')
        print(f"{i+1}: {safe_line}")

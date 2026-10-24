with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'risk', text, re.IGNORECASE)]
print(f"Total 'risk' occurrences: {len(matches)}")

# Search for functions related to risk monitoring
funcs = re.findall(r'function\s+([a-zA-Z0-9_]*risk[a-zA-Z0-9_]*)\s*\(', text, re.IGNORECASE)
print("Risk related functions:", set(funcs))

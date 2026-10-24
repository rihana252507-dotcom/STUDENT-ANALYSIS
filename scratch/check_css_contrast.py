with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = ['cyber-table', 'cyber-select', 'glass-modal', 'input-group-custom', 'badge-']
for s in sections:
    print(f"=== {s} ===")
    for m in re.finditer(rf'(\.{s}[^{{]*\{{[^}}]*\}})', text):
        print(m.group(1)[:200])
        print("---")

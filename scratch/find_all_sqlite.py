import os
import re

for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', '__pycache__', 'scratch', 'env', 'venv']):
        continue
    for f in files:
        if f.endswith(('.html', '.js')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fl:
                for line_no, line in enumerate(fl, 1):
                    if re.search(r'\bsqlite\b', line, re.IGNORECASE):
                        print(f"{path}:{line_no}: {line.strip()[:140]}")

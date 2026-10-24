import os
import re

search_patterns = [
    r'\.csv',
    r'text/csv',
    r'/api/.*export',
    r'download.*\.csv',
    r'export_csv',
    r'exportCsv',
    r'exportToCsv'
]

results = []
for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', '__pycache__', 'env', 'venv']):
        continue
    for f in files:
        if f.endswith(('.py', '.html', '.js')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fl:
                lines = fl.readlines()
                for line_idx, line in enumerate(lines, 1):
                    for pat in search_patterns:
                        if re.search(pat, line, re.IGNORECASE):
                            results.append((path, line_idx, line.strip()))
                            break

print(f"Total matching locations found: {len(results)}")
for path, line_idx, line in results:
    if not path.startswith('.\\scratch'):
        print(f"{path}:{line_idx}: {line[:120]}")

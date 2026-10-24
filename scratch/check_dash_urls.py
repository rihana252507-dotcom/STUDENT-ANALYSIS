import os

search_terms = ['/admin/dashboard', '/faculty/dashboard', '/student/dashboard', '/hod/dashboard']
for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', '__pycache__', 'env', 'venv']):
        continue
    for f in files:
        if f.endswith(('.py', '.html', '.js')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                for term in search_terms:
                    if term in c:
                        print(f'{path} contains {term}')

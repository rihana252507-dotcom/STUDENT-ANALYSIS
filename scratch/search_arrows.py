import os
import glob
import sys
sys.stdout.reconfigure(encoding='utf-8')

search_terms = ['→', '➔', '➜', '➤', '⇒', '►', '->', '-->', '&rarr;', '&#8594;', '\\u2192']
base_dir = "STUDENT-ANALYSIS"

results = []
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(('.py', '.html', '.js', '.json', '.sql')):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                    content = fl.read()
                    for term in search_terms:
                        if term in content:
                            results.append((p, term, content.count(term)))
            except Exception as e:
                pass

for r in results:
    print(repr(r))

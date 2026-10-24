with open('templates/faculty_dashboard.html', encoding='utf-8') as f:
    text = f.read()

import re
tables = re.findall(r'<table[^>]*>.*?</table>', text, re.DOTALL)
print(f"Total tables in faculty_dashboard.html: {len(tables)}")
for i, t in enumerate(tables):
    # print headers and id
    headers = re.findall(r'<th[^>]*>(.*?)</th>', t)
    tbody = re.findall(r'<tbody[^>]*id=["\'](.*?)["\']', t)
    print(f"\nTable {i+1} (tbody: {tbody}):")
    print("  Headers:", headers)

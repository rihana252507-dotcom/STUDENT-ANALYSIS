with open('templates/faculty_dashboard.html', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'<section[^>]*id=["\']([^"\']*)["\'][^>]*>', text)
print("Sections in faculty_dashboard.html:")
for m in matches:
    print(" ", m.group(1))

# Check sidebar links in faculty_dashboard.html
print("\nSidebar links:")
for m in re.finditer(r'<a[^>]*class=["\'][^"\']*sidebar-nav-link[^"\']*["\'][^>]*data-section=["\']([^"\']*)["\'][^>]*>.*?<span>(.*?)</span>', text, re.DOTALL):
    print(f"  {m.group(1)} -> {m.group(2).strip()}")

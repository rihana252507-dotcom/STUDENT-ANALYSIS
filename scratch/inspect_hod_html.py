import os
import re

path = os.path.join(os.path.dirname(__file__), "..", "templates", "hod_dashboard.html")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find all script tags
scripts = re.findall(r"<script[\s\S]*?</script>", content)
print(f"Found {len(scripts)} script tags in hod_dashboard.html")
for i, s in enumerate(scripts):
    print(f"\n--- Script {i+1} (length {len(s)}) ---")
    print(s[:500] + ("..." if len(s) > 500 else ""))

# Find all fetch calls in content
fetches = re.findall(r"fetch\([^\)]+\)", content)
print("\n--- Fetches in hod_dashboard.html ---")
for fetch in set(fetches):
    print(fetch)

# Find all section IDs
sections = re.findall(r'<section[^>]*id=["\']([^"\']+)["\']', content)
print("\n--- Sections in hod_dashboard.html ---")
print(sections)

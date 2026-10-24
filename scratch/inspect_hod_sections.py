import os
import re

path = os.path.join(os.path.dirname(__file__), "..", "templates", "hod_dashboard.html")
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Find all sections and print their headers and inner elements
sections = re.findall(r'<section\s+id="([^"]+)"[\s\S]*?</section>', html)
section_ids = re.findall(r'<section\s+id="([^"]+)"', html)
print("Section IDs:", section_ids)

for sid in section_ids:
    sec_match = re.search(r'<section\s+id="' + sid + r'"[\s\S]*?</section>', html)
    if sec_match:
        sec_text = sec_match.group(0)
        tables = re.findall(r'<tbody\s+id="([^"]+)"', sec_text)
        cards = re.findall(r'id="([^"]+)"', sec_text)
        print(f"\n=== Section: {sid} (length {len(sec_text)}) ===")
        print("  Table bodies:", tables)
        print("  Key element IDs:", [c for c in cards if not c.startswith('section-')][:15])

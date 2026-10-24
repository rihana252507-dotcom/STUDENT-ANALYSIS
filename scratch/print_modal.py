import os
import re

path = os.path.join(os.path.dirname(__file__), "..", "templates", "hod_dashboard.html")
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

modal_match = re.search(r'<div\s+id="studentDetailModal"[\s\S]*?</div>\s*</div>\s*</div>', html)
if modal_match:
    print(modal_match.group(0))

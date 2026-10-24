import os
import re

path = os.path.join(os.path.dirname(__file__), "..", "templates", "hod_dashboard.html")
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

sec_match = re.search(r'<section\s+id="section-interventions"[\s\S]*?</section>', html)
if sec_match:
    print(sec_match.group(0))

import re

with open("STUDENT-ANALYSIS/templates/admin_dashboard.html", "r", encoding="utf-8") as f:
    admin_html = f.read()

# Find overview section in admin_dashboard.html
overview_match = re.search(r'<section\s+id="section-overview"[\s\S]*?</section>', admin_html)
if overview_match:
    print("Found section-overview in admin_dashboard.html, length:", len(overview_match.group(0)))
    # print all elements with id or class containing score, attendance, kpi, or table
    overview_text = overview_match.group(0)
    ids = re.findall(r'id=["\']([^"\']+)["\']', overview_text)
    print("IDs in admin section-overview:", ids)
else:
    print("section-overview not found in admin_dashboard.html")

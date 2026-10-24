"""
Patch: Style the Excel Report button on Admin Student page.
- Change class from btn-action-secondary to btn-action-primary (blue bg, white text)
- Add inline SVG Excel/spreadsheet icon before the label
- Preserve onclick="exportCohortExcel()" and all other attributes
"""

path = "STUDENT-ANALYSIS/templates/admin_dashboard.html"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

OLD = '<button class="btn-action-secondary" onclick="exportCohortExcel()">Excel Report</button>'

NEW = (
    '<button class="btn-action-primary" onclick="exportCohortExcel()" '
    'style="background:#2F80ED; color:#ffffff;">'
    '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;">'
    '<rect x="3" y="3" width="18" height="18" rx="2"/>'
    '<line x1="3" y1="9" x2="21" y2="9"/>'
    '<line x1="3" y1="15" x2="21" y2="15"/>'
    '<line x1="9" y1="9" x2="9" y2="21"/>'
    '</svg>'
    ' Excel Report</button>'
)

if OLD not in content:
    print("ERROR: Target text not found in file.")
    import sys; sys.exit(1)

content = content.replace(OLD, NEW, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Excel Report button updated with icon and blue styling.")

# Verify
with open(path, "r", encoding="utf-8") as f:
    verify = f.read()

if "Excel Report</button>" in verify and "btn-action-primary" in verify and "exportCohortExcel" in verify:
    print("Verification PASSED: button present with correct class and onclick.")
else:
    print("Verification FAILED.")

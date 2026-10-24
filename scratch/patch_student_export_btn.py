"""
Patch: Replace the Export CSV button on Admin Student page with Excel Report button.
Only changes line 461 of admin_dashboard.html.
"""

path = "STUDENT-ANALYSIS/templates/admin_dashboard.html"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

OLD = '              <button class="btn-action-secondary" onclick="exportCohortCSV()">Export CSV</button>'
NEW = '              <button class="btn-action-secondary" onclick="exportCohortExcel()">Excel Report</button>'

if OLD not in content:
    print("ERROR: Target text not found. Aborting.")
    import sys; sys.exit(1)

count = content.count(OLD)
print(f"Found {count} occurrence(s) of target text.")

# Only replace the first occurrence that is inside the Student section
# (The overview section has its own separate Export CSV at line 218 - check if that needs preserving)
# Line 218 says: exportCohortCSV() with text "Export CSV" too, but it's in the overview hero, not students.
# We only want to replace the one inside section-students (around line 461).
# Since line 218 has "Export CSV" in a different context (hero banner), we must replace carefully.
# Count occurrences to be safe:
print(f"Occurrences: {count}")

# Replace ONLY the student-page one (should be the 2nd occurrence based on line numbers: 218 vs 461)
# Actually let's check both occurrences
idx1 = content.find(OLD)
idx2 = content.find(OLD, idx1 + 1)
print(f"First at char index: {idx1}")
print(f"Second at char index: {idx2}")

# Line 218 is in overview section (hero banner) - we keep it.
# Line 461 is in section-students - we change it.
# To identify: section-students comes after the overview section.
# The second occurrence should be line 461.

if count == 1:
    # Only one occurrence - safe to replace
    content = content.replace(OLD, NEW, 1)
    print("Replaced the single occurrence.")
elif count == 2:
    # Replace only the SECOND occurrence (student section at line 461)
    content = content[:idx2] + NEW + content[idx2 + len(OLD):]
    print("Replaced the second occurrence (student section).")
else:
    print(f"WARNING: {count} occurrences found, replacing the last one (student section).")
    # Replace the last occurrence
    last_idx = content.rfind(OLD)
    content = content[:last_idx] + NEW + content[last_idx + len(OLD):]

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done. Verifying...")

with open(path, "r", encoding="utf-8") as f:
    updated = f.read()

if NEW in updated:
    print("SUCCESS: 'Excel Report' button is now present in admin_dashboard.html.")
else:
    print("FAILURE: New button text not found.")

remaining_old = updated.count(OLD)
print(f"Remaining old 'Export CSV' occurrences pointing to exportCohortCSV: {remaining_old}")
# Should be 1 (the one in the overview hero banner that we deliberately kept)

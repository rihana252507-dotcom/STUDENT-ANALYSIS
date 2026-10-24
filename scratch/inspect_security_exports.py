import re

with open("STUDENT-ANALYSIS/app.py", "r", encoding="utf-8") as f:
    text = f.read()

print("=== ALL ROUTES WITH EXPORT ===")
for m in re.finditer(r'@app\.route\(["\']([^"\']+)["\']', text):
    route = m.group(1)
    if "export" in route:
        print(route)

print("\n=== ARROW CHARACTERS IN app.py ===")
for ch in ["\u2192", "\u2794", "\u27a4", "->", "-->", "=>", "\u2713", "\u2714", "\u25ba"]:
    cnt = text.count(ch)
    if cnt > 0:
        print(f"Found {cnt} of {repr(ch)}")

print("\n=== INTERVENTION AND STATUS IN DB ===")
import sqlite3
conn = sqlite3.connect("STUDENT-ANALYSIS/database/campusiq.db")
c = conn.cursor()
for table in ["interventions", "academic_records", "students"]:
    c.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in c.fetchall()]
    print(f"Table {table}: {cols}")
    if "status" in cols:
        c.execute(f"SELECT DISTINCT status FROM {table}")
        print(f"  Distinct statuses in {table}: {[r[0] for r in c.fetchall()]}")

conn.close()

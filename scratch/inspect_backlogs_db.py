import sqlite3

conn = sqlite3.connect('database/campusiq.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r['name'] for r in c.fetchall()]
print('Tables:', tables)

for t in ['students', 'academic_records', 'courses']:
    if t in tables:
        c.execute(f"PRAGMA table_info({t})")
        cols = [(r['name'], r['type']) for r in c.fetchall()]
        print(f"\n{t} columns:")
        for col in cols:
            print(f"  {col[0]} ({col[1]})")

# Check status values in academic_records
c.execute("SELECT DISTINCT status FROM academic_records")
statuses = [r['status'] for r in c.fetchall()]
print("\nDistinct statuses in academic_records:", statuses)

# Check backlog records
c.execute("SELECT * FROM academic_records WHERE LOWER(status) NOT IN ('passed', 'pass', 'completed', 'clear') LIMIT 5")
backlogs = [dict(r) for r in c.fetchall()]
print(f"\nSample backlog records ({len(backlogs)}):")
for b in backlogs:
    print(" ", b)

# Check students with backlogs
c.execute("SELECT student_id, name, backlogs FROM students WHERE backlogs > 0 LIMIT 5")
s_backlogs = [dict(r) for r in c.fetchall()]
print("\nStudents with backlogs > 0:")
for s in s_backlogs:
    print(" ", s)
    # Check what academic_records exist for this student
    c.execute("SELECT * FROM academic_records WHERE student_id = ?", (s['student_id'],))
    records = [dict(r) for r in c.fetchall()]
    print(f"    Total academic records: {len(records)}")
    for rec in records:
        print(f"      Course: {rec.get('course_name')} ({rec.get('course_code')}), Sem: {rec.get('semester')}, Grade: {rec.get('grade')}, Status: {rec.get('status')}")

conn.close()

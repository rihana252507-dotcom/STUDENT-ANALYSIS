import sqlite3

conn = sqlite3.connect('database/campusiq.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT * FROM students WHERE user_id='student001' OR student_id='CIQ-2026-001'")
s = dict(c.fetchone())
print("Student:", s['name'], s['student_id'], "Attendance:", s['attendance_pct'])

c.execute("SELECT * FROM academic_records WHERE student_id = ? ORDER BY semester DESC, id ASC", (s['student_id'],))
recs = [dict(r) for r in c.fetchall()]
print(f"Total academic records: {len(recs)}")
for r in recs[:8]:
    print(" ", r.get('course_name'), f"({r.get('course_code')})", "classes:", r.get('classes_attended'), "/", r.get('classes_conducted'), "att%:", r.get('attendance_pct'), "status:", r.get('status'))

conn.close()

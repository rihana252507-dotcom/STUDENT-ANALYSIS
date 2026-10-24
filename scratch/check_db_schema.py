import sqlite3

conn = sqlite3.connect('database/campusiq.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("Tables in campusiq.db:", tables)

for t in ['students', 'academic_records', 'interventions']:
    if t in tables:
        c.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in c.fetchall()]
        print(f"Columns in {t}:", cols)
conn.close()

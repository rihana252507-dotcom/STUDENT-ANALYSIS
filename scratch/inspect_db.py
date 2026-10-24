import sqlite3

conn = sqlite3.connect('database/campusiq.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
print('Tables:', tables)

for t in tables:
    cursor.execute(f"PRAGMA table_info({t});")
    cols = cursor.fetchall()
    print(f"\nColumns of {t}:", [(c[1], c[2]) for c in cols])

print("\n--- Users sample ---")
cursor.execute("SELECT id, username, role, department FROM users LIMIT 10;" if 'department' in [c[1] for c in cursor.execute("PRAGMA table_info(users);").fetchall()] else "SELECT id, username, role FROM users LIMIT 10;")
print(cursor.fetchall())

print("\n--- Distinct roles in users ---")
cursor.execute("SELECT DISTINCT role FROM users;")
print(cursor.fetchall())

print("\n--- Distinct departments in students ---")
if 'students' in tables:
    cursor.execute("SELECT DISTINCT department FROM students;")
    print(cursor.fetchall())

print("\n--- Distinct departments in faculty ---")
if 'faculty' in tables:
    cursor.execute("SELECT DISTINCT department FROM faculty;")
    print(cursor.fetchall())

print("\n--- Interventions sample ---")
if 'interventions' in tables:
    cursor.execute("SELECT * FROM interventions LIMIT 3;")
    print(cursor.fetchall())

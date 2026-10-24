import sqlite3

conn = sqlite3.connect('database/campusiq.db')
cursor = conn.cursor()

print("--- Departments ---")
cursor.execute("SELECT * FROM departments;")
for d in cursor.fetchall():
    print(d)

print("\n--- Users (user_id, role, name, department) ---")
cursor.execute("SELECT user_id, role, name, department FROM users;")
for u in cursor.fetchall():
    print(u)

print("\n--- Faculty (faculty_id, user_id, name, department) ---")
cursor.execute("SELECT faculty_id, user_id, name, department FROM faculty;")
for f in cursor.fetchall():
    print(f)

print("\n--- Students department counts ---")
cursor.execute("SELECT department, count(*) FROM students GROUP BY department;")
for s in cursor.fetchall():
    print(s)

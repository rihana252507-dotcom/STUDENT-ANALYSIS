import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "database", "campusiq.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("PRAGMA table_info(users)")
print("users cols:", [col["name"] for col in c.fetchall()])

c.execute("SELECT user_id, email, name, role, department FROM users WHERE role = 'hod'")
hod_users = [dict(r) for r in c.fetchall()]
print(f"HOD users in DB ({len(hod_users)}):", hod_users)

c.execute("SELECT DISTINCT role FROM users")
print("All roles in DB:", [r["role"] for r in c.fetchall()])

c.execute("SELECT user_id, name, role, department FROM users")
print("All users:", [dict(r) for r in c.fetchall()])

c.execute("SELECT * FROM departments")
print("Departments:", [dict(r) for r in c.fetchall()])

conn.close()

import sqlite3
conn = sqlite3.connect('database/campusiq.db')
c = conn.cursor()
c.execute("SELECT user_id, role, department FROM users WHERE role='student' LIMIT 5")
print('Sample students:', c.fetchall())
c.execute("SELECT user_id, role, department FROM users WHERE role='faculty' LIMIT 5")
print('Sample faculty:', c.fetchall())

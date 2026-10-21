import sqlite3

conn = sqlite3.connect(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\database\campusiq.db')
c = conn.cursor()
c.execute("SELECT user_id, role, name FROM users WHERE role = 'faculty' LIMIT 5")
print("Faculty users:", c.fetchall())
c.execute("SELECT user_id, role, name FROM users WHERE role = 'student' LIMIT 5")
print("Student users:", c.fetchall())

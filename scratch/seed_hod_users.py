import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database/campusiq.db')
cursor = conn.cursor()

hod_pass = generate_password_hash("Hod@123")

hod_accounts = [
    ("hod_cse", hod_pass, "hod", "Dr. Sunita Rao (HOD CSE)", "hod.cse@campusiq.edu", "CSE"),
    ("hod_aiml", hod_pass, "hod", "Dr. Priya Krishnaswamy (HOD AIML)", "hod.aiml@campusiq.edu", "AIML"),
    ("hod_ece", hod_pass, "hod", "Dr. Amit Verma (HOD ECE)", "hod.ece@campusiq.edu", "ECE"),
    ("hod_it", hod_pass, "hod", "Dr. Meenakshi Sundaram (HOD IT)", "hod.it@campusiq.edu", "IT"),
]

for uid, phash, role, name, email, dept in hod_accounts:
    cursor.execute("SELECT id FROM users WHERE user_id = ?", (uid,))
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?, role = ?, name = ?, email = ?, department = ?
            WHERE user_id = ?
        """, (phash, role, name, email, dept, uid))
        print(f"Updated existing user {uid}")
    else:
        cursor.execute("""
            INSERT INTO users (user_id, password_hash, role, name, email, department)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (uid, phash, role, name, email, dept))
        print(f"Inserted new user {uid}")

conn.commit()

# Verify
cursor.execute("SELECT user_id, role, name, department FROM users WHERE role = 'hod';")
print("\nHOD users in database:")
for u in cursor.fetchall():
    print(u)

conn.close()

import os
import sqlite3
from werkzeug.security import generate_password_hash

db_path = os.path.join(os.path.dirname(__file__), "..", "database", "campusiq.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

hod_data = [
    ("hod_cse", "Hod@123", "Dr. Sunita Rao (HOD CSE)", "hod.cse@campusiq.edu", "CSE"),
    ("hod_aiml", "Hod@123", "Dr. Priya Krishnaswamy (HOD AIML)", "hod.aiml@campusiq.edu", "AIML"),
    ("hod_ece", "Hod@123", "Dr. Amit Verma (HOD ECE)", "hod.ece@campusiq.edu", "ECE"),
    ("hod_it", "Hod@123", "Dr. Meenakshi Sundaram (HOD IT)", "hod.it@campusiq.edu", "IT"),
    ("hod_aids", "Hod@123", "Prof. Neha Gupta (HOD AI&DS)", "hod.aids@campusiq.edu", "AI&DS"),
    ("hod_me", "Hod@123", "Dr. K. S. Pillai (HOD ME)", "hod.me@campusiq.edu", "ME"),
]

added = []
for h_user, h_pass, h_name, h_email, h_dept in hod_data:
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_id = ?", (h_user,))
    if cursor.fetchone()["count"] == 0:
        h_pass_hash = generate_password_hash(h_pass)
        cursor.execute("""
        INSERT INTO users (user_id, password_hash, role, name, email, department)
        VALUES (?, ?, 'hod', ?, ?, ?)
        """, (h_user, h_pass_hash, h_name, h_email, h_dept))
        added.append(h_user)

conn.commit()
conn.close()

print(f"Added HOD accounts: {added if added else 'None (all already exist)'}")

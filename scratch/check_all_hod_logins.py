import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app
from database.db import get_db

app.config["TESTING"] = True
client = app.test_client()

conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT user_id, department, email FROM users WHERE role = 'hod'")
hods = cursor.fetchall()
conn.close()

passwords_to_try = ["Hod@123", "Admin@123", "Faculty@123", "Student@123"]

for h in hods:
    uid = h["user_id"]
    dept = h["department"]
    found_pass = None
    for p in passwords_to_try:
        resp = client.post("/login", json={"user_id": uid, "password": p})
        if resp.status_code == 200:
            found_pass = p
            break
    print(f"HOD User: {uid} (Dept: {dept}) -> Password: {found_pass}")

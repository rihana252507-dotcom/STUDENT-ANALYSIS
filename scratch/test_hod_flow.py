import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app
import json

app.config["TESTING"] = True
client = app.test_client()

print("--- 1. Testing HOD Login with Form POST ---")
resp = client.post("/login", data={"username": "hod_cse", "password": "Hod@123"}, follow_redirects=False)
print("Form POST status:", resp.status_code)
print("Form POST headers Location:", resp.headers.get("Location"))

print("\n--- 2. Testing HOD Login with JSON POST ---")
client = app.test_client()
resp = client.post("/login", json={"user_id": "hod_cse", "password": "Hod@123"})
print("JSON POST status:", resp.status_code)
print("JSON POST response:", resp.get_json())

print("\n--- 3. Testing GET /hod ---")
resp = client.get("/hod")
print("GET /hod status:", resp.status_code)
if resp.status_code != 200:
    print("GET /hod redirect location:", resp.headers.get("Location"))
else:
    print("GET /hod content length:", len(resp.data))

print("\n--- 4. Testing GET /api/hod/overview ---")
resp = client.get("/api/hod/overview")
print("GET /api/hod/overview status:", resp.status_code)
if resp.status_code == 200:
    data = resp.get_json()
    print("Keys in overview response:", list(data.keys()))
    print("Department:", data.get("department"))
    print("Metrics:", data.get("metrics"))
    print("Faculty count:", len(data.get("faculty", {}).get("list", [])))
    print("Students count:", len(data.get("students", [])))
    print("Interventions count:", len(data.get("interventions", [])))
else:
    print("Overview response text:", resp.data.decode("utf-8")[:500])

print("\n--- 5. Testing Inspect Student as HOD ---")
# Student in CSE
resp = client.get("/api/students/CIQ-2026-001")
print("CSE student CIQ-2026-001 status:", resp.status_code)
# Student NOT in CSE (e.g. IT student CIQ-2026-002)
resp2 = client.get("/api/students/CIQ-2026-002")
print("IT student CIQ-2026-002 status:", resp2.status_code)
if resp2.status_code != 200:
    print("IT student response:", resp2.get_json())
else:
    print("IT student returned data:", resp2.get_json().get("student_id"), resp2.get_json().get("department"))

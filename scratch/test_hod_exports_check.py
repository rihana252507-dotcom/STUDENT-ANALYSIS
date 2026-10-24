import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app

app.config["TESTING"] = True
client = app.test_client()
client.post("/login", json={"user_id": "hod_cse", "password": "Hod@123"})

endpoints = [
    "/api/hod/export/students/csv",
    "/api/hod/export/students/xlsx",
    "/api/hod/export/faculty/csv",
    "/api/hod/export/faculty/xlsx",
    "/api/hod/export/summary/csv",
    "/api/hod/export/summary/xlsx",
]

for ep in endpoints:
    resp = client.get(ep)
    print(f"{ep}: status {resp.status_code}, length {len(resp.data)}, content-type: {resp.headers.get('Content-Type')}")

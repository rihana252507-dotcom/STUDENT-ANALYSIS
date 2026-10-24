import os

auth_py = os.path.join(os.path.dirname(__file__), "..", "services", "auth.py")
with open(auth_py, "r", encoding="utf-8") as f:
    print("--- services/auth.py ---")
    print(f.read())

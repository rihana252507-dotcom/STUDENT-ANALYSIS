import ast
import re

with open("STUDENT-ANALYSIS/app.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's find all route definitions and their following decorators and function names
pattern = r'(@app\.route\([^)]+\)\s*(?:@\w+(?:\([^)]*\))?\s*)*def\s+(\w+)\s*\([^)]*\):)'
matches = re.finditer(pattern, text)

for m in matches:
    block = m.group(1)
    fn_name = m.group(2)
    lines = block.strip().split("\n")
    route_line = [l.strip() for l in lines if l.strip().startswith("@app.route")]
    login_req = any("login_required" in l for l in lines)
    role_req = [l.strip() for l in lines if "role_required" in l]
    print(f"Fn: {fn_name:30} | Route: {route_line[0] if route_line else 'None'} | LoginReq: {login_req} | Roles: {role_req}")

with open("STUDENT-ANALYSIS/app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines):
    if "def log_intervention" in line:
        print(f"Found 'def log_intervention' at index {i+1}")
        for j in range(max(0, i-5), min(len(lines), i+15)):
            print(f"{j+1}: {lines[j]}", end="")

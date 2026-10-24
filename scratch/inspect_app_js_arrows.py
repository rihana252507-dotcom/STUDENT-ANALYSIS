import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("STUDENT-ANALYSIS/static/js/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "&rarr;" in line or "→" in line or "Completed" in line:
        print(f"{i+1}: {line.strip()}")

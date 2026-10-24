with open('static/js/app.js', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if 'document.getElementById("academicPerfTableBody")' in l:
        print(f"academicPerfTableBody at line {i}")
        for j in range(max(0, i-5), min(len(lines), i+60)):
            print(f"{j+1}: {lines[j].rstrip()}")
        break

for i, l in enumerate(lines, 1):
    if 'document.getElementById("riskAlertsTableBody")' in l:
        print(f"\nriskAlertsTableBody at line {i}")
        for j in range(max(0, i-5), min(len(lines), i+60)):
            print(f"{j+1}: {lines[j].rstrip()}")
        break

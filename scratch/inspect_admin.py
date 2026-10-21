with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'id="section-ai-insights"' in l:
        print(f"Found section at line {i+1}")
        for j in range(i, min(i + 150, len(lines))):
            print(f"{j+1}: {lines[j].rstrip()}")
        break

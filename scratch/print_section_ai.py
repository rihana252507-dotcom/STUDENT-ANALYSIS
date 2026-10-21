with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '<section id="section-ai-insights"' in l:
        print(f"Starting at {i+1}")
        for j in range(i, min(i+70, len(lines))):
            print(f"{j+1}: {lines[j].rstrip()}")
        break

with open('static/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if any(k in line for k in ['switchSection', 'data-section', 'section-risk-monitoring', 'section-settings', 'section-placement', 'section-reports']):
        print(f"{idx}: {line.strip()[:120]}")

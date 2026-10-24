with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

import re
selectors = ['.hero-glass-banner', '.glass-kpi-card', '.kpi-title-label', '.kpi-big-value']
for sel in selectors:
    idx = text.find(sel)
    if idx != -1:
        print(text[idx:idx+300])
        print("="*40)

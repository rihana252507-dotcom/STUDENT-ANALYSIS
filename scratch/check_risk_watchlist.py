with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'id="riskWatchlistBody"', text)
if m:
    print("Found riskWatchlistBody at", m.start())
    print(text[m.start()-200:m.start()+300])

with open('static/js/app.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

m2 = re.search(r'function renderRiskWatchlist', js_text)
if m2:
    print("Found renderRiskWatchlist at", m2.start())
    safe = js_text[m2.start():m2.start()+1500].encode('ascii', 'replace').decode('ascii')
    print(safe)

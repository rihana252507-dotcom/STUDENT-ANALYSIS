with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
keywords = ['ai-insights', 'segment', 'low risk', 'attendance', 'segcount', 'segmentcards']
for line_no, line in enumerate(text.splitlines()):
    if any(k in line.lower() for k in keywords):
        print(f"{line_no+1}: {line[:120]}")

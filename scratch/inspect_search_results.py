import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('static/js/app.js', encoding='utf-8') as f:
    text = f.read()

idx = text.find('Sem ${s.semester}</div>')
print(text[idx:idx+1500])

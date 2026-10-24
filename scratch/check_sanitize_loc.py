with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('def _sanitize_csv_cell')
print(text[idx:idx+800])

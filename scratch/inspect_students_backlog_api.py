with open('app.py', encoding='utf-8') as f:
    text = f.read()

idx = text.find('actual_backlogs = max(s.get("backlogs") or 0, rec_count)')
print(text[idx-100:idx+800])
